from pydantic import BaseModel


class Settings(BaseModel):
    gtfs_rt_url: str = "https://api.data.gov.my/gtfs-realtime/vehicle-position/prasarana"
    redis_url: str = "redis://localhost:6379/0"
    poll_interval_seconds: int = 30


settings = Settings()
