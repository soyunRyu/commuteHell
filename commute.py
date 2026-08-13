from mcp.server import MCPServer

from holiday import get_day_off_info
from scoring import (
    calculate_commute_difficulty,
    calculate_transfer_fatigue,
    calculate_travel_time_score,
    calculate_walking_burden,
    calculate_weather_discomfort,
)
from transit import get_transit_route
from weather import fetch_weather

mcp = MCPServer("commuteHell")

@mcp.tool()
def get_commute_difficulty(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
) -> dict:
    """출발지와 도착지 좌표로 퇴근 난이도를 계산합니다."""
    route = get_transit_route( #출퇴근 경로 조회
        start_lat,
        start_lon,
        end_lat,
        end_lon,
    )
    weather = fetch_weather(end_lat, end_lon) #날씨 조회
    day_off = get_day_off_info() #오늘 주말인지 공휴일인지 확인

    scores = {
        "travel_time": calculate_travel_time_score(
            route["total_minutes"]
        ),
        "transfer": calculate_transfer_fatigue(
            route["transfer_count"]
        ),
        "walking": calculate_walking_burden(
            route["walking_minutes"],
            route["walking_distance_meters"],
        ),
        "weather": calculate_weather_discomfort(
            weather["discomfort_index"]
        ),
    }

    difficulty = calculate_commute_difficulty(
        travel_time_score=scores["travel_time"],
        transfer_score=scores["transfer"],
        walking_score=scores["walking"],
        weather_score=scores["weather"],
        day_off_info=day_off,
    )

    return {
        "route": route,
        "weather": weather,
        "day_off": day_off,
        "difficulty": difficulty,
    }


if __name__ == "__main__":
    mcp.run()