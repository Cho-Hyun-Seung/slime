from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from models import TouristSpot
from config import Settings
import aiohttp
import asyncio
from urllib.parse import unquote
import csv

async def get_tourist_spots(
    page_no: int,
    parent_code: int, 
    sigungu_code: int,
    num_of_rows: int,
    category_code: str,
    settings: Settings,
):
    category_arr = category_code.split(',')
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
    tourist_spots_list = []
    params_arr = []
    
    params = {
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "MobileOS": "ETC",
        "MobileApp": "ETC",
        "serviceKey": api_key,
        "_type": "json",
        "contentTypeId": 12
    }
    
    if sigungu_code:
        if parent_code == 0:
            params["areaCode"] = sigungu_code
        else:
            params["areaCode"] = parent_code
            params["sigunguCode"] = sigungu_code
            
    if category_arr:
        for category in category_arr:
            new_params = params.copy()
            new_params['cat1'] = category[:3]
            new_params["cat2"] = category[:5]
            new_params["cat3"] = category[:9]
            params_arr.append(new_params)
    else:
        params_arr.append(params)

    try:
        async with aiohttp.ClientSession() as aiohttp_session:
            for params in params_arr:
                async with aiohttp_session.get(url, params=params, timeout=10) as response:
                    response.raise_for_status()
                    data = await response.json()
                    body = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    
                    for item in body:
                        content_id = item["contentid"]
                        result = {
                            "title": item.get("title", ""),
                            "first_image": item.get("firstimage", ""),
                            "addr1": item.get("addr1", ""),
                            "content_id": content_id,
                            "mapx": item.get("mapx"),
                            "mapy": item.get("mapy")
                        }
                        
                        tourist_spots_list.append(result)
            
            return tourist_spots_list

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")


async def get_tourist_spot_detail(session: Session , content_id: int, settings: Settings):
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
        "defaultYN": "Y",
        "addrinfoYN": "Y"
    }
    
    try:
        async with aiohttp.ClientSession() as aiohttp_session:
            async with aiohttp_session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                item_list = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                if item_list:
                    item = item_list[0]
                    result = {
                        "title": item.get("title", "No Title"),
                        "first_image": item.get("firstimage", ""),
                        "addr1": item.get("addr1", "No Address"),
                        "content_id": item.get("contentid"),
                        "mapx": item.get("mapx"),
                        "mapy": item.get("mapy"),
                        "overview": item.get("overview", "No Overview"),
                    }
                    
                    spot_eval = session.exec(select(TouristSpot).where(TouristSpot.content_id == content_id)).first()
                    if spot_eval:
                        result["negative"] = spot_eval.negative
                        result["positive"] = spot_eval.positive
                        result["total_review"] = spot_eval.total_review
                    return result
                else:
                    raise HTTPException(status_code=404, detail="Item not found in the response")

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")


async def get_nearby_tourist_spot(map_x: float, map_y: float, settings: Settings, radius = 10000, num_of_rows = 4):
    api_key = unquote(settings.TOUR_API_KEY)
    url = "http://apis.data.go.kr/B551011/KorService1/locationBasedList1"
    params = {
        "numOfRows": num_of_rows,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "ETC",
        "serviceKey": api_key,
        "_type": "json",
        "contentTypeId": 12,
        "mapX": map_x,
        "mapY": map_y,
        "radius": radius,
        "arrange": "E"
    }
    
    try:
        async with aiohttp.ClientSession() as aiohttp_session:
            async with aiohttp_session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                body = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                tourist_spots_list = [
                    {
                        "title": item.get("title", ""),
                        "first_image": item.get("firstimage", ""),
                        "addr1": item.get("addr1", ""),
                        "content_id": item.get("contentid"),
                        "dist": item.get("dist"),
                        "mapx": item.get("mapx"),
                        "mapy": item.get("mapy")
                    }
                    for item in body[1:]  # 0번 인덱스 제외
                ]
                
                return tourist_spots_list

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timed out")
