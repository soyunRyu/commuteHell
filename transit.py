from datetime import datetime
import requests
from config import COMMUTE_URL, TMAP_API_KEY

def get_transit_route( # TMAP 대중교통 API를 호출하여 최적 경로 정보를 조회
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
) -> dict:
    """TMAP 대중교통 API에서 최적 경로 정보를 조회합니다."""
    response = requests.post(
        COMMUTE_URL,
        headers={
            "accept": "application/json",
            "appKey": TMAP_API_KEY,
            "content-type": "application/json",
        },
        json={
            "startX": str(start_lon),
            "startY": str(start_lat),
            "endX": str(end_lon),
            "endY": str(end_lat),
            "format": "json",
            "count": 10,
            "searchDttm": datetime.now().strftime("%Y%m%d%H%M"),
        },
        timeout=15,
    )

    if not response.ok:
        raise RuntimeError(
            f"status={response.status_code}, "
            f"body={response.text}, "
            f"url={response.url}, "
            f"key_length={len(TMAP_API_KEY)}, "
            f"key_last4={TMAP_API_KEY[-4:]}"
        )

    result = response.json()

    itineraries = (
        result.get("metaData", {})
        .get("plan", {})
        .get("itineraries", [])
    )

    if not itineraries:
        raise ValueError("이동 가능한 대중교통 경로가 없습니다.")

    route = min(
        itineraries,
        key=lambda item: item.get("totalTime", float("inf")),
    )

    return {
    "total_minutes": round(
        route.get("totalTime", 0) / 60,
        1,
    ),
    "walking_minutes": round(
        route.get("walkTime", 0) / 60,
        1,
    ),
    "walking_distance_meters": float(
        route.get("walkDistance", 0)
    ),
    "transfer_count": int(
        route.get("transferCount", 0)
    ),
    "fare": route.get("fare", {}),
}