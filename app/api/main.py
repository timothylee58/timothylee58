import json

from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.config import settings
from app.services.realtime_ingestor import RealtimeIngestor

app = FastAPI(title="Rapid KL Transit Intelligence")

STATIONS = [
    {
        "station_id": "KJ16",
        "station_name": "KLCC",
        "latitude": 3.1586,
        "longitude": 101.7123,
    },
    {
        "station_id": "SBK20",
        "station_name": "Muzium Negara",
        "latitude": 3.1343,
        "longitude": 101.6866,
    },
]

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
ingestor = RealtimeIngestor(redis_client=redis_client, stations=STATIONS)


@app.on_event("startup")
async def on_startup() -> None:
    await ingestor.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await ingestor.stop()
    await redis_client.close()


@app.get("/live-map")
async def live_map() -> list[dict]:
    raw = await redis_client.get("live:vehicles")
    return json.loads(raw) if raw else []


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
