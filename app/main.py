from functools import lru_cache
from time import sleep
from fastapi import FastAPI, HTTPException, Depends, Query
import uvicorn
from sqlalchemy.orm import Session
from typing import List
import logging

# from get_pona import get_pona
from get_planner import get_planner
from models import Category, Region 
from database import get_session
from get_category import get_category_by_code, get_root_category, get_descendants_category
from get_spots import get_tourist_spots, get_tourist_spot_detail, get_nearby_tourist_spot
from get_region import get_root_regions, get_child_regions
from get_festivals import get_festival_detail, get_festivals
import config
from get_comment import get_youtube_comments
from typing import Annotated


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings 객체를 캐싱하여 처음 한 번만 불러오게 설정
@lru_cache
def get_settings():
    return config.Settings()

app = FastAPI()
SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/touristspot")
async def get_tourist_spot(
    page_no: int = Query(1, description="페이지 번호"),
    parent_code: int = Query(33, description="도 코드"), 
    sigungu_code: int = Query(None,description="시군구 코드"),
    num_of_rows: int  = Query(5,description="한 페이지 관광지 개수"),
    category_code:str = Query(''),
    settings: config.Settings = Depends(get_settings),
):
    try:
        tourist_spots = await get_tourist_spots(page_no=page_no, parent_code=parent_code, category_code=category_code,
                                                sigungu_code=sigungu_code, settings=settings, num_of_rows = num_of_rows)
        return tourist_spots
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/touristspot/detail")
async def get_tourist_spot_details(
    session:SessionDep,
    content_id:int=Query(None,description="고유번호"),
    settings: config.Settings = Depends(get_settings)
):
    try:
        tourist_spot_detail = await get_tourist_spot_detail(session, content_id,settings)
        return tourist_spot_detail
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/touristspot/nearby")
async def get_nearby_tourist_spots(
    map_x:float = Query(None), 
    map_y:float = Query(None), 
    settings: config.Settings = Depends(get_settings)
):
    try:
        tourist_spots = await get_nearby_tourist_spot(map_x,map_y,settings)
        return tourist_spots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/comments")
def fetch_comments(video_id: str = Query(..., description="video_id는 필수입니다."), 
                   settings: config.Settings = Depends(get_settings)):
    try:
        # video_id가 빈 문자열인 경우
        if not video_id.strip():
            raise HTTPException(status_code=400, detail="video_id는 필수입니다.")
        
        # video_id로 YouTube API에서 댓글 가져오기
        comments = get_youtube_comments(video_id, settings)
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/category", response_model=Category)
def category_by_code(
    session: SessionDep,
    category_code: str = Query(default=None)
):
    logger.info("카테고리 조회 요청이 들어왔습니다. 코드: %s", category_code) 
    category = get_category_by_code(session, code = category_code)

    if not category:
        logger.error("카테고리를 찾을 수 없습니다. 코드: %s", category_code) 
        raise HTTPException(status_code=404, detail="Category not found") 
    
    return category  

# 루트 카테고리 가져오기 엔드포인트
@app.get("/category/roots", response_model=List[Category])
def root_category(session:SessionDep):
    try:
        # 루트 카테고리를 가져옴
        return get_root_category(session)
    except HTTPException as e:
        # HTTPException을 그대로 전달
        raise e
    except Exception as e:
        # 기타 예외 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail=f"Error fetching root categories: {str(e)}")

# 특정 카테고리의 하위 카테고리 가져오기 엔드포인트
@app.get("/category/descendants", response_model=List[Category])
def descendants_category( session:SessionDep,parent_code: str = Query(None)):
    category = get_descendants_category(session, parent_code)

    if not category:
        logger.error("자식 카테고리를 찾을 수 없습니다. 코드: %s", parent_code) 
        raise HTTPException(status_code=404, detail="Category not found") 
    
    return category  

@app.get("/region/roots", response_model=List[Region])
async def get_root_region(session:SessionDep):
    regions = get_root_regions(session)
    
    if not regions:
        logger.error("루트 지역을 찾을 수 없습니다")
        raise HTTPException(status_code=404, detail="root region not found") 
    return regions

@app.get("/region/childs", response_model=List[Region])
async def get_child_region(session:SessionDep, parent_code:int = Query(None)):
    regions = get_child_regions(session, parent_code)
    
    if not regions:
        logger.error("자식 지역을 찾을 수 없습니다")
        raise HTTPException(status_code=404, detail="child region not found") 
    return regions

# 임시용으로 사용
# @app.get("/region/getroot")
# async def get_root(session:SessionDep,areaCode:int=Query(None),settings: config.Settings = Depends(get_settings)):
#     region = await get_roots(session, settings,areaCode)
    
    return region

@app.get("/festival")
async def get_festival(
        page_no:int = Query(1), 
        num_of_rows:int = Query(100),
        parent_code:int = Query(None),
        sigungu_code: int = Query(None,description="시군구 코드"),
        event_start_date = Query(None),
        event_end_date = Query(None),
        settings: config.Settings = Depends(get_settings)
):
    try:
        festivals = await get_festivals(
            page_no, parent_code, num_of_rows, sigungu_code, event_start_date, event_end_date,settings)
        return festivals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/festival/detail")
async def get_festival_details(
    content_id:int=Query(None,description="고유번호"),
    settings: config.Settings = Depends(get_settings)
):
    try:
        festival_detail = await get_festival_detail(content_id,settings)
        return festival_detail
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get('/pona')
# def get_ponas(session:SessionDep):
#     data = get_pona(session)
#     return data

@app.get('/planner')
async def planner(
    session: SessionDep,     
    map_x: float = Query(None), 
    map_y: float = Query(None), 
    settings: config.Settings = Depends(get_settings),
):
    planner = []
    distances = 0

    # 초기 데이터를 가져옴
    data = await get_planner(map_x, map_y, settings=settings, session=session)
    if data:
        planner.append(data[0])
        distances += float(data[0]['dist'])
        
    visited_content_ids = [data[0]['content_id']]

    iteration_counter = 0
    # 새로운 데이터를 추가할 때, 중복 여부 확인
    while distances <= 30000:
        # 현재 플래너의 마지막 위치 정보를 사용하여 추가로 데이터 가져오기
        if len(planner) == 0:
            break
        iteration_counter +=1
        if(iteration_counter >=20):
            break
        
        last_place = planner[-1]
        new_data = await get_planner(
            map_x=last_place["mapx"],
            map_y=last_place["mapy"],
            settings=settings,
            session=session
        )
        
        if not new_data:
            print("더 이상 추가할 데이터가 없습니다.")
            break
        print('new!!'+ str(distances))
        for spot in new_data:
            if spot["content_id"] not in visited_content_ids:
                distances += float(spot["dist"])
                planner.append(spot)
                visited_content_ids.append(spot["content_id"])
                break
    return planner

# main 함수에서 환경 설정 값을 사용
def main():
    settings = get_settings()  # 캐싱된 설정 값 사용
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.EXTERNAL_PORT), reload=True)

if __name__ == "__main__":
    main()
