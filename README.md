# CommuteHell

출발지와 도착지의 대중교통 경로, 날씨, 환승 횟수, 도보 부담 등을 종합하여 **퇴근 난이도**를 계산하는 Python MCP 서버입니다.

## 주요 기능

- 항목별 점수를 합산한 퇴근 난이도 제공 
- TMAP 대중교통 경로 조회
- 총 이동시간 및 환승 횟수 조회
- 도보시간 및 도보거리 조회
- 기상청 초단기예보 조회
- 기온·습도·강수 기반 불쾌지수 계산
- 주말 및 법정공휴일 확인



## 퇴근 난이도 산정 기준

퇴근 난이도는 총 100점으로 계산합니다.

| 항목 | 최대 점수 | 산정 기준 |
|---|---:|---|
| 이동시간 부담 | 30점 | 70분을 부담도 100%로 계산 |
| 환승 피로도 | 25점 | 환승 4회를 부담도 100%로 계산 |
| 도보 부담 | 20점 | 도보시간 70%, 도보거리 30% 반영 |
| 날씨 불쾌도 | 20점 | 불쾌지수 100을 부담도 100%로 계산 |
| 금요일·공휴일 보정 | 5점 | 평일 5점, 금요일·공휴일 0점 |

```text
퇴근 난이도
= 이동시간 부담 30점
+ 환승 피로도 25점
+ 도보 부담 20점
+ 날씨 불쾌도 20점
+ 금요일·공휴일 보정 5점
```

## 사용 API

### TMAP 대중교통 API

출발지와 도착지 사이의 대중교통 경로를 조회합니다.

| 항목 | 내용 |
|---|---|
| 제공 기관 | SK Open API |
| API | TMAP 대중교통 경로 요약정보 |
| 요청 방식 | `POST` |
| 인증 방식 | `appKey` 요청 헤더 |
| 사용 파일 | `transit.py` |

```text
https://apis.openapi.sk.com/transit/routes/sub/
```

주요 사용 데이터:

- 총 이동시간
- 환승 횟수
- 도보시간
- 도보거리
- 대중교통 요금

### 기상청 초단기예보 API

도착지 좌표를 기준으로 현재와 가까운 시간의 날씨를 조회합니다.

| 항목 | 내용 |
|---|---|
| 제공 기관 | 기상청·공공데이터포털 |
| API | 초단기예보조회 |
| 요청 방식 | `GET` |
| 응답 형식 | XML |
| 사용 파일 | `weather.py` |

```text
https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst
```

주요 사용 데이터:

- 기온
- 습도
- 하늘 상태
- 강수 형태 및 강수량
- 풍속
- 낙뢰 정보

위도·경도는 기상청 API에서 사용하는 격자 좌표로 변환하여 요청합니다.

### 한국천문연구원 특일정보 API

오늘이 법정공휴일인지 확인합니다.

| 항목 | 내용 |
|---|---|
| 제공 기관 | 한국천문연구원·공공데이터포털 |
| API | 국경일·공휴일 정보 |
| 요청 방식 | `GET` |
| 사용 파일 | `holiday.py` |

```text
https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo
```

토요일과 일요일은 API를 호출하지 않고 Python 날짜 정보로 판단합니다.

## 기술 스택

| 구분 | 기술 |
|---|---|
| 언어 | Python |
| 패키지 관리 | uv |
| MCP SDK | `mcp` |
| MCP 전송 방식 | stdio |
| HTTP 통신 | requests |
| XML 변환 | xmltodict |
| 환경변수 관리 | python-dotenv |
| 외부 연결 | Smithery Uplink |
| 버전 관리 | Git, GitHub |

## 주요 Python 패키지

| 패키지 | 용도 |
|---|---|
| `mcp[cli]` | MCP 서버와 Tool 구현 |
| `requests` | TMAP·기상청·공휴일 API 호출 |
| `xmltodict` | 기상청 XML 응답을 Python 딕셔너리로 변환 |
| `python-dotenv` | `.env` 파일에서 API 키 로딩 |
| `uv` | 가상환경과 의존성 관리 |

## 시스템 구성

```text
Claude CLI
    │
    │ MCP tools/call
    ▼
CommuteHell MCP Server
    ├─ TMAP 대중교통 API
    ├─ 기상청 초단기예보 API
    ├─ 한국천문연구원 공휴일 API
    └─ 퇴근 난이도 점수 계산
```

## 실행 환경

- Python 3.14
- MCP Python SDK 2.x
- Windows
- stdio 기반 MCP 서버
- Claude Desktop 또는 Claude CLI
- Smithery CLI/Uplink 지원

## 환경변수

| 변수 | 용도 |
|---|---|
| `TMAP_API_KEY` | TMAP 대중교통 API 인증 |
| `OPENDATA_API_KEY` | 기상청 및 공휴일 API 인증 |

```env
TMAP_API_KEY=발급받은_TMAP_키
OPENDATA_API_KEY=발급받은_공공데이터포털_키
```

API 키가 들어 있는 `.env` 파일은 Git에 포함하지 않습니다.

## 프로젝트 구조

```text
commuteHell/
├─ src/
│  └─ commutehell/
│     ├─ __init__.py
│     ├─ server.py
│     ├─ config.py
│     ├─ transit.py
│     ├─ weather.py
│     ├─ holiday.py
│     └─ scoring.py
├─ .env
├─ .gitignore
├─ .python-version
├─ pyproject.toml
├─ uv.lock
└─ README.md
```

## 함수 호출 구조

```text
Claude CLI
└─ MCP tools/call 요청
   └─ commute.py
      └─ get_commute_difficulty() [MCP Tool]
         ├─ transit.py
         │  └─ get_transit_route()
         │     └─ TMAP API
         │
         ├─ weather.py
         │  └─ fetch_weather()
         │     ├─ st_forecast()
         │     │  ├─ get_wheather_time()
         │     │  ├─ convert_to_grid()
         │     │  └─ 기상청 API
         │     └─ summarize_weather()
         │        ├─ calculate_discomfort_index()
         │        ├─ get_discomfort_level()
         │        ├─ format_precipitation()
         │        ├─ add_unit()
         │        └─ make_weather_summary()
         │
         ├─ holiday.py
         │  └─ get_day_off_info()
         │     └─ 공휴일 API
         │
         └─ scoring.py
            ├─ calculate_travel_time_score()
            │  └─ clamp()
            ├─ calculate_transfer_fatigue()
            │  └─ clamp()
            ├─ calculate_walking_burden()
            │  └─ clamp()
            ├─ calculate_weather_discomfort()
            │  └─ clamp()
            └─ calculate_commute_difficulty()
               └─ calculate_day_score()
```

## 파일별 역할

| 파일 | 역할 |
|---|---|
| `commute.py` | MCP 서버 실행 및 공개 Tool 관리 |
| `config.py` | 환경변수, API 키, API URL 관리 |
| `transit.py` | TMAP 대중교통 경로 조회 |
| `weather.py` | 기상청 예보 조회 및 불쾌지수 계산 |
| `holiday.py` | 주말 및 법정공휴일 확인 |
| `scoring.py` | 항목별 점수 및 최종 퇴근 난이도 계산 |

## 환경 설정

### 1. 저장소 내려받기

```bash
git clone https://github.com/soyunRyu/commuteHell.git
cd commuteHell
```

### 2. 의존성 설치

이 프로젝트는 `uv`를 사용합니다.

```bash
uv sync
```

### 3. 환경변수 설정

프로젝트 최상위에 `.env` 파일을 만들고 API 키를 입력합니다.

```env
OPENDATA_API_KEY=공공데이터포털_API_키
TMAP_API_KEY=TMAP_API_키
```

> `.env`에는 실제 API 키가 포함되므로 GitHub에 커밋하지 마세요.

## 실행

```bash
uv run commutehell
```

또는 가상환경 실행 파일을 직접 사용할 수 있습니다.

```bash
.venv/Scripts/commutehell.exe
```

## MCP Tool

### `get_commute_difficulty`

출발지와 도착지 좌표를 받아 퇴근 난이도를 계산합니다.

#### 입력값

| 이름 | 형식 | 설명 |
|---|---|---|
| `start_lat` | `float` | 출발지 위도 |
| `start_lon` | `float` | 출발지 경도 |
| `end_lat` | `float` | 도착지 위도 |
| `end_lon` | `float` | 도착지 경도 |

#### 호출 예시

```json
{
  "start_lat": 37.5569,
  "start_lon": 126.8643,
  "end_lat": 37.5503,
  "end_lon": 126.9158
}
```

사용자가 지역명이나 주소를 입력하면 MCP 클라이언트가 먼저 좌표를 찾은 뒤 이 Tool을 호출합니다.

## Smithery Uplink 연결

```cmd
smithery mcp add --id commutehell --force -- "D:\my_mcp\commuteHell\.venv\Scripts\commutehell.exe"
```

Uplink가 실행되는 동안 로컬 MCP 서버를 Smithery를 통해 사용할 수 있습니다.

## 참고 자료

- [MCP 블로그 시리즈](https://toyourlight.tistory.com/category/%F0%9F%97%9C%20MCP?page=4)
- [MCP에 대한 이해와 나만의 미니 프로젝트 만들기](https://velog.io/@cjungy2/MCP%EC%97%90-%EB%8C%80%ED%95%9C-%EC%9D%B4%ED%95%B4%EC%99%80-%EB%82%98%EB%A7%8C%EC%9D%98-mini-Project-%EB%A7%8C%EB%93%A4%EA%B8%B0)
- [Model Context Protocol Quickstart](https://glama.ai/blog/2024-11-25-model-context-protocol-quickstart)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
- [WikiDocs MCP 자료](https://wikidocs.net/286574)
