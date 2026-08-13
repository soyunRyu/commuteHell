from .config import OPENDATA_API_KEY, WEATHER_URL
import math
from datetime import datetime, timedelta
import requests
import xmltodict


"""""
fetch_weather()
├─ st_forecast()
├─ summarize_weather()
├─  calculate_discomfort_index()
└─ make_weather_summary()
"""""

PTY_CODES = { #강수코드
    "0": "강수 없음",
    "1": "비",
    "2": "비 또는 눈",
    "3": "눈",
    "4": "소나기",
    "5": "빗방울",
    "6": "빗방울 또는 눈날림",
    "7": "눈날림",
}

RAIN_DISCOMFORT_PENALTY = { #비에 따른 불쾌지수 가산점
    "0": 0,
    "1": 5,
    "2": 5,
    "3": 2,
    "4": 7,
    "5": 2,
    "6": 2,
    "7": 2,
}

SKY_CODES = {
    "1": "맑음",
    "3": "구름 많음",
    "4": "흐림",
}

LGT_CODES = {
    "0": "낙뢰 없음",
    "1": "낙뢰 가능성 낮음",
    "2": "낙뢰 가능성 보통",
    "3": "낙뢰 가능성 높음",
}

def fetch_weather(lat: float, lon: float) -> dict: #위도와 경도를 받아서 날씨 정보를 조회하고 요약하여 반환
    data = st_forecast(OPENDATA_API_KEY, WEATHER_URL, lat, lon) #기상청 API 호출

    departure_date, departure_time = get_wheather_time() #시간 설정
    target_at = datetime.strptime(
        departure_date + departure_time,
        "%Y%m%d%H%M",
    )

    return summarize_weather(data, target_at) #날씨 요약 정보 생성


def st_forecast(api_key, url, lat, lon) : #api_key, url, lat, lon를 받아서 기상청 API 호출 후 데이터 반환
    date, time = get_wheather_time()

    grid = convert_to_grid(lat, lon)
    nx = grid['x']
    ny = grid['y']

    parameters = {'serviceKey': api_key,
                  'numOfRows': '100',
                    'pageNo': '1',
                    'dataType': 'XML',
                    'base_date': date,
                    'base_time': time,
                    'nx': nx,
                    'ny': ny}
    response = requests.get(url, params=parameters, timeout=10)
    data = xmltodict.parse(response.text)

    return data

def get_wheather_time() :  #초단기예보를 위한 시간 설정 
    now = datetime.now()

    if now.minute < 45:
        now -= timedelta(hours=1)

    return now.strftime("%Y%m%d"), now.strftime("%H30")

def convert_to_grid(lat, lon) : #위도 경도를 격자 좌표로 변환
    lat = float(lat)
    lon = float(lon)

    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기준점 Y좌표(GRID)

    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn * math.cos(slat1)) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)
    
    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / (ra ** sn)
    
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    
    x = (ra * math.sin(theta)) + XO + 1.5
    y = (ro - ra * math.cos(theta)) + YO + 1.5
    
    return {'x': int(x), 'y': int(y)}

def summarize_weather(data, target_at=None): #response 데이터를 받아서 날씨 요약 정보 반환
    response = data.get("response")

    if not response:
        error = data.get("OpenAPI_ServiceResponse", {})
        message = error.get("cmmMsgHeader", {}).get(
            "returnAuthMsg",
            "올바르지 않은 기상청 API 응답입니다.",
        )
        raise RuntimeError(message)

    header = response.get("header", {})

    if header.get("resultCode") != "00":
        raise RuntimeError(
            f"기상청 API 오류: "
            f"{header.get('resultMsg', '알 수 없는 오류')}"
        )

    items = (
        response.get("body", {})
        .get("items", {})
        .get("item", [])
    )

    if isinstance(items, dict):
        items = [items]

    if not items:
        raise ValueError("날씨 예보 데이터가 없습니다.")

    available_times = sorted({
        datetime.strptime(
            item["fcstDate"] + item["fcstTime"],
            "%Y%m%d%H%M",
        )
        for item in items
    })

    if target_at is None:
        selected_time = available_times[0]
    else:
        selected_time = min(
            available_times,
            key=lambda value: abs(value - target_at),
        )

    target_date = selected_time.strftime("%Y%m%d")
    target_time = selected_time.strftime("%H%M")

    values = {
        item["category"]: item["fcstValue"]
        for item in items
        if item["fcstDate"] == target_date
        and item["fcstTime"] == target_time
    }

    temperature = values.get("T1H")
    humidity = values.get("REH")
    pty_code = values.get("PTY")

    discomfort_index, rain_penalty = calculate_discomfort_index(
        temperature,
        humidity,
        pty_code,
    )

    weather = {
        "forecast_at": selected_time.strftime("%Y-%m-%d %H:%M"),
        "sky": SKY_CODES.get(values.get("SKY"), "정보 없음"),
        "precipitation_type": PTY_CODES.get(
            values.get("PTY"),
            "정보 없음",
        ),
        "precipitation": format_precipitation(
            values.get("RN1")
        ),
        "temperature": add_unit(values.get("T1H"), "°C"),
        "humidity": add_unit(values.get("REH"), "%"),
        "wind_speed": add_unit(values.get("WSD"), "m/s"),
        "lightning": LGT_CODES.get(
            values.get("LGT"),
            "정보 없음",
        ),
        "discomfort_index": discomfort_index,
        "discomfort_level": get_discomfort_level(
            discomfort_index
        ),
        "rain_penalty": rain_penalty,
    }

    weather["summary"] = make_weather_summary(weather)
    return weather

def add_unit(value, unit): #값에 단위를 붙여서 반환
    return "정보 없음" if value is None else f"{value}{unit}"

def format_precipitation(value): #강수량 값에 단위를 붙여서 반환
    if value is None:
        return "정보 없음"

    if value in {"강수없음", "강수 없음", "0"}:
        return "없음"

    return value if "mm" in value else f"{value}mm"

def calculate_discomfort_index(temperature, humidity, pty_code):#불쾌지수 계산
    if temperature is None or humidity is None:
        return None, 0

    temperature = float(temperature)
    humidity = float(humidity)

    base_index = (
        0.81 * temperature
        + 0.01 * humidity * (0.99 * temperature - 14.3)
        + 46.3
    )

    rain_penalty = int(
        RAIN_DISCOMFORT_PENALTY.get(str(pty_code), 0)
    )

    final_index = round(
        base_index + rain_penalty,
        1,
    )

    return final_index, rain_penalty

def get_discomfort_level(index):#불쾌지수 반환
    if index is None:
        return "정보 없음"
    if index < 55:
        return "추움"
    if index < 60:
        return "쌀쌀"
    if index < 70:
        return "쾌적"
    if index < 75: 
        return "조금 더움"
    if index < 80:
        return "더움"
    return "매우 더움"

def make_weather_summary(weather): #날씨 요약 정보 생성
    if weather["discomfort_index"] is None:
        discomfort_summary = "불쾌지수는 계산할 수 없습니다."
    else:
        penalty_summary = ""

        if weather["rain_penalty"] > 0:
            penalty_summary = (
                f", 강수 가산 +{weather['rain_penalty']}점 적용"
            )

        discomfort_summary = (
            f"'{weather['discomfort_level']}' 단계로"
            f"불쾌지수는 {weather['discomfort_index']} 입니다. "
           
            f"({penalty_summary.lstrip(', ')})."
            if penalty_summary
            else
            f"'{weather['discomfort_level']}' 단계로 "
            f"불쾌지수는 {weather['discomfort_index']} 입니다. "
        )

    return (
        f"{weather['forecast_at']} 기준, "
        f"하늘은 {weather['sky']}이고 "
        f"{weather['precipitation_type']} 상태입니다. "
        f"기온은 {weather['temperature']}, "
        f"습도는 {weather['humidity']}, "
        f"시간당 강수량은 {weather['precipitation']}, "
        f"{weather['lightning']}, "
        f"풍속은 {weather['wind_speed']}입니다. "
        f"{discomfort_summary}"
    )

