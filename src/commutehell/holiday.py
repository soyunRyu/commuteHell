from datetime import datetime
import requests
from .config import HOLIDAY_URL, OPENDATA_API_KEY

def get_day_off_info(target_date=None) -> dict: #오늘이 주말인지 법정공휴일인지 확인
    """주말 또는 법정공휴일인지 확인합니다."""
    target_date = target_date or datetime.now().date()

    if target_date.weekday() >= 5:
        return {
            "is_day_off": True,
            "reason": "주말",
        }

    response = requests.get(
        HOLIDAY_URL,
        params={
            "ServiceKey": OPENDATA_API_KEY,
            "solYear": target_date.strftime("%Y"),
            "solMonth": target_date.strftime("%m"),
            "_type": "json",
            "numOfRows": 50,
        },
        timeout=10,
    )
    response.raise_for_status()

    result = response.json()["response"]
    header = result["header"]

    if header["resultCode"] != "00":
        raise RuntimeError(
            f"공휴일 API 오류: {header['resultMsg']}"
        )

    items = result.get("body", {}).get("items")

    if not items:
        return {
            "is_day_off": False,
            "reason": "평일",
        }

    holidays = items.get("item", [])
    if isinstance(holidays, dict):
        holidays = [holidays]

    date_number = int(target_date.strftime("%Y%m%d"))

    for holiday in holidays:
        if (
            int(holiday["locdate"]) == date_number
            and holiday["isHoliday"] == "Y"
        ):
            return {
                "is_day_off": True,
                "reason": holiday["dateName"],
            }

    return {
        "is_day_off": False,
        "reason": "평일",
    }