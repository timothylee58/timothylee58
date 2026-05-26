from typing import Literal

from pydantic import BaseModel


OccupancyEnum = Literal[
    "EMPTY",
    "MANY_SEATS_AVAILABLE",
    "FEW_SEATS_AVAILABLE",
    "STANDING_ROOM_ONLY",
    "CRUSHED_STANDING_ROOM_ONLY",
    "FULL",
    "NOT_ACCEPTING_PASSENGERS",
    "NO_DATA_AVAILABLE",
]


class VehicleState(BaseModel):
    vehicle_id: str
    trip_id: str | None = None
    route_id: str | None = None
    latitude: float
    longitude: float
    timestamp: int | None = None
    occupancy_status: OccupancyEnum = "NO_DATA_AVAILABLE"
    nearest_station_id: str | None = None
    nearest_station_name: str | None = None
    distance_meters: float | None = None
