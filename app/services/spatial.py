import math
from collections.abc import Sequence


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(
        d_lam / 2
    ) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_station(
    vehicle_lat: float,
    vehicle_lon: float,
    stations: Sequence[dict],
) -> tuple[str | None, str | None, float | None]:
    if not stations:
        return None, None, None

    min_idx = min(
        range(len(stations)),
        key=lambda idx: haversine_meters(
            vehicle_lat,
            vehicle_lon,
            stations[idx]["latitude"],
            stations[idx]["longitude"],
        ),
    )
    station = stations[min_idx]
    dist = haversine_meters(
        vehicle_lat,
        vehicle_lon,
        station["latitude"],
        station["longitude"],
    )
    return station["station_id"], station["station_name"], dist
