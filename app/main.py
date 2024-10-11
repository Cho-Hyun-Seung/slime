from functools import lru_cache
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from sqlalchemy.orm import Session
from typing import List
import logging

from models import Category, Region 
from database import get_session
from get_category import get_category_by_code, get_root_category, get_descendants_category
from get_spots import get_tourist_spots
from get_region import get_root_regions, get_child_regions
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

from fastapi import FastAPI, Depends, HTTPException, Query
import config  # 설정 파일 가져오기
from get_comment import get_youtube_comments  # YouTube 댓글 가져오는 함수

@app.get("/touristspot")
async def get_tourist_spot(
    page_no: int = Query(1, description="페이지 번호"),
    do_code: int = Query(33, description="도 코드"), 
    sigungu_code: int = Query(None,description="시군구 코드"),
    num_of_rows: int  = Query(5,description="한 페이지 관광지 개수"),
    settings: config.Settings = Depends(get_settings)
):
    try:
        tourist_spots = await get_tourist_spots(page_no=page_no, do_code=do_code, 
                                                sigungu_code=sigungu_code, settings=settings, num_of_rows = num_of_rows)
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
async def get_child_region(session:SessionDep, parent_region:str = Query(None)):
    regions = get_child_regions(session, parent_region)
    
    if not regions:
        logger.error("루트 지역을 찾을 수 없습니다")
        raise HTTPException(status_code=404, detail="root region not found") 
    return regions


# main 함수에서 환경 설정 값을 사용
def main():
    settings = get_settings()  # 캐싱된 설정 값 사용
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.EXTERNAL_PORT), reload=True)

if __name__ == "__main__":
    main()
