import json
import os

import requests
from functools import lru_cache
from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, Depends
from fastapi import Form, Query, File
from typing import Annotated

import config


# Settings 객체를 처음 한번에 불러옴
@lru_cache
def get_settings():
    return config.Settings()

    
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}




# main 함수에서 환경 설정 값을 사용
def main(settings: Annotated[config.Settings, Depends(get_settings)]):
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(settings.EXTERNAL_PORT), reload=True)

if __name__ == "__main__":
    main(get_settings())