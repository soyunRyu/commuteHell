import os
import urllib.parse

from dotenv import load_dotenv

load_dotenv( r"D:\my_mcp\commuteHell\.env", override=True,)

OPENDATA_API_KEY = os.environ["OPENDATA_API_KEY"].strip()
TMAP_API_KEY = os.environ["TMAP_API_KEY"].strip()

WEATHER_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
HOLIDAY_URL = ("https://apis.data.go.kr/B090041/openapi/service/" "SpcdeInfoService/getRestDeInfo")
COMMUTE_URL = "https://apis.openapi.sk.com/transit/routes/sub/"