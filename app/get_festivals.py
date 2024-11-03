from fastapi import Depends, HTTPException
from config import Settings
import aiohttp
import asyncio
from urllib.parse import unquote
import datetime as dt

# region이 있는 경우 region별로 요청
async def get_festivals(
        page_no, 
        parent_code:int,
        num_of_rows:int,
        sigungu_code: int,
        event_start_date,
        event_end_date,
        settings:Settings
):
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"
    now = dt.datetime.now()
    # 현재 날짜 -1년 축제 부터 불러옴!
    one_year_ago = now.replace(year=now.year - 1)
    now_date = f"{one_year_ago.year}{one_year_ago.month:02d}{one_year_ago.day:02d}"
    festivals = []
    event_start_date = event_start_date.replace('-','')
    event_end_date  = event_end_date.replace('-','')
    # A02070100 : 문화 관광 축제
    # A02070200 : 일반 축제
    # 얘네들만 가져와야 함!
    params = {
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "ETC",  # 오타 수정
        "serviceKey": api_key,
        "_type": "json",
        "eventStartDate": event_start_date,
    }
    if sigungu_code:
        if parent_code == 0:
            params["areaCode"] = sigungu_code
        else:
            params["areaCode"] = parent_code
            params["sigunguCode"] = sigungu_code
    """
    1. http 요청
    
    2. 카테고리로 컷하기
    
    3. 날짜로 컷하기
    """
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                item_list = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                result = []
                if item_list:
                   item = item_list[0]
                   result = [
                       {
                            "title": item.get("title","No Title"),
                            "first_image": item.get("firstimage", ""),
                            "addr1": item.get("addr1", "No Address"),
                            "content_id": item.get("contentid", None),
                            "cat2": item.get("cat2"),
                            "event_start_date": item.get("eventstartdate"),
                            "event_end_date":item.get("eventenddate")
                        # 축제 시작일, 종료일 필터링
                        } for item in item_list if item["cat2"] == "A0207" and dt.datetime.strptime(item["eventenddate"],"%Y%m%d") <= dt.datetime.strptime(event_end_date,"%Y%m%d")]
                   return result
                else:
                    raise HTTPException(status_code=404, detail="Item not found in the response")  # 아이템이 없을 경우

                
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")  # 예외 처리
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out") 


async def get_festival_detail(content_id: int, settings: Settings):
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/detailCommon1"
    params = {
        "numOfRows": 10,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "ETC",
        "serviceKey": api_key,
        "_type": "json",
        "firstImageYN": "Y",
        "mapinfoYN": "Y",
        "contentId": content_id,
        "overviewYN": "Y",
        "defaultYN":"Y",
        "addrinfoYN":"Y"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                
                # 안전하게 중첩된 값 추출
                item_list = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                # 아이템 리스트가 비어있지 않은지 확인
                if item_list:
                    item = item_list[0]
                    result = {
                        "title": item.get("title", "No Title"),
                        "first_image": item.get("firstimage", ""),
                        "addr1": item.get("addr1", "No Address"),
                        "content_id": item.get("contentid", None),
                        "mapx": item.get("mapx", None),
                        "mapy": item.get("mapy", None),
                        "overview": item.get("overview", "No Overview"),
                    }
                    return result
                else:
                    raise HTTPException(status_code=404, detail="Item not found in the response")  # 아이템이 없을 경우

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")  # 클라이언트 오류 예외 처리
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")  # 타임아웃 예외 처리



async def get_carousel_item(
    num_of_rows:int,
    event_start_date,
    event_end_date,
    settings:Settings
):
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"