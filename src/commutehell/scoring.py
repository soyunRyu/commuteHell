from datetime import datetime

TRAVEL_MAX_MINUTES = 70
TRANSFER_MAX_COUNT = 4
WALKING_MAX_MINUTES = 30
WALKING_MAX_METERS = 1000
DISCOMFORT_MAX_INDEX = 100


def calculate_commute_difficulty( #출퇴근 난이도를 계산
    travel_time_score: float,
    transfer_score: float,
    walking_score: float,
    weather_score: float,
    day_off_info: dict,
) -> dict:
    """항목별 점수를 합산해 최종 퇴근 난이도를 반환합니다."""
    day_result = calculate_day_score(day_off_info)

    final_score = (
        clamp(travel_time_score, 0, 30)
        + clamp(transfer_score, 0, 25)
        + clamp(walking_score, 0, 20)
        + clamp(weather_score, 0, 20)
        + day_result["score"]
    )
    final_score = round(clamp(final_score, 0, 100), 1)

    if final_score < 30:
        level = "쉬움"
    elif final_score < 50:
        level = "보통"
    elif final_score < 70:
        level = "어려움"
    else:
        level = "매우 어려움"

    return {
        "score": final_score,
        "level": level,
        "components": {
            "travel_time": {
                "score": travel_time_score,
                "maximum": 30,
            },
            "transfer_fatigue": {
                "score": transfer_score,
                "maximum": 25,
            },
            "walking_burden": {
                "score": walking_score,
                "maximum": 20,
            },
            "weather_discomfort": {
                "score": weather_score,
                "maximum": 20,
            },
            "day_adjustment": {
                "score": day_result["score"],
                "maximum": 5,
                "applied": day_result["applied"],
                "reason": day_result["reason"],
            },
        },
    }

def clamp( #값을 최소값과 최대값 사이로 제한
    value: float,
    minimum: float = 0,
    maximum: float = 100,
) -> float:
    return max(minimum, min(float(value), maximum))


def calculate_travel_time_score(
    total_minutes: float,
) -> float:
    """70분을 100%로 보고 최대 30점을 반영합니다."""
    burden_ratio = (
        max(float(total_minutes), 0)
        / TRAVEL_MAX_MINUTES
    )

    score = burden_ratio * 30
    return round(clamp(score, 0, 30), 1)


def calculate_transfer_fatigue(
    transfer_count: int,
) -> float:
    """환승 4회를 100%로 보고 최대 25점을 반영합니다."""
    burden_ratio = (
        max(int(transfer_count), 0)
        / TRANSFER_MAX_COUNT
    )

    score = burden_ratio * 25
    return round(clamp(score, 0, 25), 1)


def calculate_walking_burden(
    walking_minutes: float,
    walking_distance_meters: float,
) -> float:
    """
    도보시간 30분과 거리 1,000m를 각각 100%로 계산합니다.

    시간 비율 70%, 거리 비율 30%를 반영하여
    최대 20점을 반환합니다.
    """
    time_ratio = (
        max(float(walking_minutes), 0)
        / WALKING_MAX_MINUTES
    )
    time_ratio = clamp(time_ratio, 0, 1)

    distance_ratio = (
        max(float(walking_distance_meters), 0)
        / WALKING_MAX_METERS
    )
    distance_ratio = clamp(distance_ratio, 0, 1)

    walking_ratio = (
        time_ratio * 0.70
        + distance_ratio * 0.30
    )

    score = walking_ratio * 20
    return round(clamp(score, 0, 20), 1)


def calculate_weather_discomfort(
    discomfort_index: float | None,
) -> float:
    """불쾌지수 100을 100%로 보고 최대 20점을 반영합니다."""
    if discomfort_index is None:
        return 0.0

    burden_ratio = (
        max(float(discomfort_index), 0)
        / DISCOMFORT_MAX_INDEX
    )

    score = burden_ratio * 20
    return round(clamp(score, 0, 20), 1)


def calculate_day_score(
    day_off_info: dict,
) -> dict:
    """평일은 5점, 금요일 또는 공휴일은 0점입니다."""
    is_friday = datetime.now().weekday() == 4
    is_day_off = bool(
        day_off_info.get("is_day_off", False)
    )

    if is_day_off:
        return {
            "score": 0.0,
            "applied": True,
            "reason": day_off_info.get("reason", "공휴일"),
        }

    if is_friday:
        return {
            "score": 0.0,
            "applied": True,
            "reason": "금요일",
        }

    return {
        "score": 5.0,
        "applied": False,
        "reason": "평일",
    }

