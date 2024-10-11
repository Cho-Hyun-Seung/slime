from fastapi import HTTPException
from sqlmodel import Session, select, and_
from models import Region
from config import Settings
import aiohttp
import asyncio
from urllib.parse import unquote


def get_root_regions(session: Session) -> list[Region]:
    # 시군구 코드가 없는 root 지역들 가져오기
    root_regions = session.exec(select(Region).where(Region.sigungu_code.is_(None))).all()
    return root_regions

def get_child_regions(session: Session, parent_region: str) -> list[Region]:
    # 부모 지역 찾기
    parent_region_obj = session.exec(select(Region).where(Region.region == parent_region)).first()
    if parent_region_obj is None:
        raise HTTPException(status_code=404, detail="모지역이 없습니다!")
    
    # 부모 지역의 area_code를 기반으로 자식 지역들 찾기
    child_regions = session.exec(select(Region)
                                 .where(and_(Region.area_code == parent_region_obj.area_code, 
                                             Region.sigungu_code.is_not(None)))).all()
    return child_regions

# 임시용으로 사용
# async def get_roots(session: Session, settings: Settings, areaCode: int):
#     api_key = unquote(settings.TOUR_API_KEY)
#     url = "http://apis.data.go.kr/B551011/KorService1/areaCode1"

#     params = {
#         "numOfRows": 100,
#         "MobileOS": "ETC",
#         "MobileApp": "ETC",
#         "serviceKey": api_key,
#         "_type": "json",
#         "areaCode": areaCode,
#     }

#     try:
#         async with aiohttp.ClientSession() as http_session:
#             async with http_session.get(url, params=params, timeout=10) as response:
#                 response.raise_for_status()
#                 data = await response.json()
#                 body = data.get("response", {}).get("body").get("items", {}).get("item", [])
                
#                 new_regions = [Region(region=item["name"], area_code=areaCode, sigungu_code=int(item["code"])) 
#                                for item in body]

#                 if new_regions:
#                     session.add_all(new_regions)
#                     session.commit()


#                 return new_regions

#     except aiohttp.ClientError as e:
#         raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
#     except asyncio.TimeoutError:
#         raise HTTPException(status_code=408, detail="Request timed out")