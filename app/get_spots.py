from fastapi import Depends, HTTPException
from config import Settings
import aiohttp
import asyncio
from urllib.parse import unquote

async def get_tourist_spots(page_no: int, do_code: int, sigungu_code: int, settings: Settings):
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
    
    params = {
        "numOfRows": "10",
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "ETC",  # 오타 수정
        "serviceKey": api_key,
        "_type": "json",
        "areaCode": do_code,
    }
    if sigungu_code:
        params["sigunguCode"] = sigungu_code
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                return data

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")  # 예외 처리
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")  # 타임아웃 예외 처리
