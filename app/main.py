from functools import lru_cache
from fastapi import FastAPI, HTTPException, Depends
import uvicorn

from get_spots import get_tourist_spots
import config
from get_comment import get_youtube_comments

# Settings 객체를 캐싱하여 처음 한 번만 불러오게 설정
@lru_cache
def get_settings():
    return config.Settings()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

from fastapi import FastAPI, Depends, HTTPException, Query
import config  # 설정 파일 가져오기
from get_comment import get_youtube_comments  # YouTube 댓글 가져오는 함수

@app.get("/touristspot")
async def get_tourist_spot(
    page_no: int = Query(1, description="Page number for pagination"),
    do_code: int = Query("33", description="Province code"), 
    sigungu_code: int = Query(None,description="City/district code"),  # Default to "000"
    settings: config.Settings = Depends(get_settings)
):
    try:
        tourist_spots = await get_tourist_spots(page_no=page_no, do_code=do_code, sigungu_code=sigungu_code, settings=settings)
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


# main 함수에서 환경 설정 값을 사용
def main():
    settings = get_settings()  # 캐싱된 설정 값 사용
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.EXTERNAL_PORT), reload=True)

if __name__ == "__main__":
    main()
