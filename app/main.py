from functools import lru_cache
from fastapi import FastAPI, HTTPException, Depends
import uvicorn

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

@app.get("/comments/{video_id}")
def fetch_comments(video_id: str, settings: config.Settings = Depends(get_settings)):
    try:
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
