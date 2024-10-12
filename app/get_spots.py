from fastapi import Depends, HTTPException
from config import Settings
import aiohttp
import asyncio
from urllib.parse import unquote

async def get_tourist_spots(page_no: int, do_code: int, sigungu_code: int,num_of_rows:int, settings: Settings):
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
    tourist_spots_list = []
    
    params = {
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "ETC",  # 오타 수정
        "serviceKey": api_key,
        "_type": "json",
        "areaCode": do_code,
        "contentTypeId": 12
    }
    if sigungu_code:
        params["sigunguCode"] = sigungu_code
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                body = data.get("response",{}).get("body").get("items").get("item",[])
                result = [{"title": item["title"], 
                           "first_image":item["firstimage"], 
                           "addr1":item["addr1"],
                           "content_id": item["contentid"],
                           "mapx":item["mapx"],
                           "mapy":item["mapy"] } for item in body]
                tourist_spots_list += result
                
                return tourist_spots_list

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")  # 예외 처리
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")  # 타임아웃 예외 처리

async def get_tourist_spot_detail(content_id: int, settings: Settings):
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


async def get_nearby_tourist_spot(map_x: float,map_y: float, settings:Settings):
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/locationBasedList1"
    params = {
        "numOfRows": 4,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "ETC",
        "serviceKey": api_key,
        "_type": "json",
        "contentTypeId": 12,
        "mapX": map_x,
        "mapY": map_y,
        "radius": 10000,
        "arrange":"E"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                tourist_spots_list = []
                body = data.get("response",{}).get("body").get("items").get("item",[])
                result = [
                    {
                        "title": item["title"], 
                        "first_image": item["firstimage"], 
                        "addr1": item["addr1"],
                        "content_id": item["contentid"],
                        "dist": item["dist"],
                        "mapx": item["mapx"],
                        "mapy": item["mapy"]
                    } 
                    for item in body[1:]  # 0번 인덱스 제외
                ]
                tourist_spots_list += result
                
                return tourist_spots_list
                
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")  # 클라이언트 오류 예외 처리
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")  # 타임아웃 예외 처리