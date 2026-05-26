import asyncio
import json
import time

import httpx
from google.transit import gtfs_realtime_pb2
from redis.asyncio import Redis

from app.core.config import settings
from app.models.schemas import VehicleState
from app.services.spatial import nearest_station


class RealtimeIngestor:
    def __init__(self, redis_client: Redis, stations: list[dict]):
        self.redis = redis_client
        self.stations = stations
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        self._stop_event.clear()
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is not None:
            await self._task

    async def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                states = await self.fetch_and_transform()
                await self.cache_states(states)
            except Exception:
                pass
            await asyncio.sleep(settings.poll_interval_seconds)

    async def fetch_and_transform(self) -> list[VehicleState]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(settings.gtfs_rt_url)
            response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        now = int(time.time())

        states: list[VehicleState] = []
        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue
            vehicle = entity.vehicle
            if not vehicle.HasField("position"):
                continue

            occupancy = vehicle.occupancy_status
            occupancy_name = (
                gtfs_realtime_pb2.VehiclePosition.OccupancyStatus.Name(occupancy)
                if occupancy is not None
                else "NO_DATA_AVAILABLE"
            )

            station_id, station_name, distance_m = nearest_station(
                vehicle.position.latitude,
                vehicle.position.longitude,
                self.stations,
            )

            states.append(
                VehicleState(
                    vehicle_id=vehicle.vehicle.id or entity.id,
                    trip_id=vehicle.trip.trip_id if vehicle.HasField("trip") else None,
                    route_id=vehicle.trip.route_id if vehicle.HasField("trip") else None,
                    latitude=vehicle.position.latitude,
                    longitude=vehicle.position.longitude,
                    timestamp=vehicle.timestamp or now,
                    occupancy_status=occupancy_name,
                    nearest_station_id=station_id,
                    nearest_station_name=station_name,
                    distance_meters=distance_m,
                )
            )
        return states

    async def cache_states(self, states: list[VehicleState]) -> None:
        payload = [state.model_dump() for state in states]
        await self.redis.set("live:vehicles", json.dumps(payload), ex=120)
