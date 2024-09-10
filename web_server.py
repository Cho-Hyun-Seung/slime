import json
import tempfile
import os

import requests
from fastapi import FastAPI, Request, Response, HTTPException, UploadFile
from fastapi import Form, Query, File
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from pymongo import MongoClient

with open(".env", "r") as f:
    config = json.load(f)

web = FastAPI()
templates = Jinja2Templates(directory="templates/")

@web.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@web.post("/login")
def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    body = { "username": username, "password": password }
    ret = requests.post(f"http://127.0.0.1:{int(config['INTERNAL_PORT'])}/api/login", data=body)
    ret = json.loads(ret.text)
    
    if ret["status"] == 200:
        response.set_cookie(key="token", value=ret["detail"])
        response.headers["location"] = "/main"
        response.status_code = 303
        return response
    else:
        raise HTTPException(status_code=404, detail="Invalid username or password")
    
@web.get("/register")
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@web.post("/register")
def post_register(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    data = { "username": username, "password": password }
    ret = requests.post(f"http://127.0.0.1:{int(config['INTERNAL_PORT'])}/api/user", data=data)
    ret = json.loads(ret.text)
    
    if ret["status"] == 201:
        response.headers["location"] = "/"
        response.status_code = 303
        return response
    else:
        raise HTTPException(status_code=500, detail="Invalid username or password")

@web.get("/main")
def index(request: Request):
    ret = requests.get(f"http://127.0.0.1:{int(config['INTERNAL_PORT'])}/api/post")
    ret = json.loads(ret.text)

    return templates.TemplateResponse("main.html", { "request": request, "posts": ret["detail"] })

@web.get("/post/{pid}")
def index(request: Request, pid: int):
    ret = requests.get(f"http://127.0.0.1:{int(config['INTERNAL_PORT'])}/api/post/{pid}")
    ret = json.loads(ret.text)

    if ret["status"] == 200:
        return templates.TemplateResponse("detail.html", { "request": request, "post": ret["detail"] })
    else:
        raise HTTPException(status_code=404, detail="Post not found")
    
@web.post("/post")
async def index(request: Request, response: Response, title: str = Form(...), body: str = Form(...), file: UploadFile = File(None)):
    data = {"title": title, "body": body, "token": request.cookies["token"] }

    if file and file.size != 0 and file.content_type == "text/plain":
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, file.filename)

        with open(tmp_path, "wb") as f:
            while chunk := await file.read(8192):
                f.write(chunk)

        attachments_path = os.path.join("./attachments/", file.filename)
        os.system(f"mv -n {tmp_path} {attachments_path}")
        data["attachment"] = attachments_path

    ret = requests.post(f"http://127.0.0.1:{int(config['INTERNAL_PORT'])}/api/post", data=data)
    ret = json.loads(ret.text)
    
    if ret["status"] == 400:
        response.headers["location"] = f"/"
        response.status_code = 303
        return response

    if ret["status"] == 201:
        response.headers["location"] = f"/main"
        response.status_code = 303
        return response
    else:
        raise HTTPException(status_code=500, detail="Failed to upload post")
    
@web.get("/search")
def index(request: Request, response: Response, url: str = Query(..., alias="q")):
    if url[:4] != "http":
        url = f"http://127.0.0.1:{config['INTERNAL_PORT']}/api/post/{url}"

    try:
        ret = requests.get(url)
        ret.raise_for_status()
        ret = json.loads(ret.text)
    except Exception as e:
        return templates.TemplateResponse("fallback.html", { "request": request, "url": url })

    return templates.TemplateResponse("detail.html", { "request": request, "post": ret["detail"] })

@web.get("/greet")
def index(request: Request, q: str = Query(...)):
    return Template(f"Hello, {q}!").render()

@web.get("/ping")
def index(request: Request, q: str = Query(...)):
    import subprocess
    return subprocess.run(f"ping -c 3 {q}", shell=True, text=True, capture_output=True)

@web.get("/blind")
def index(request: Request, sql: str = Query(...)):
        ret = requests.get(f"http://127.0.0.1:{config['INTERNAL_PORT']}/api/query?sql={sql}")
        ret = json.loads(ret.text)
        return ret

@web.get("/nosql")
def index(request: Request, sql: str = Query(...)):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["test"]
        users = db["users"]
        return { "status": 200, "detail": users.find_one(json.loads(sql))["username"] }
    except:
        return { "status": 500, "detail": "" }

def main():
    import uvicorn
    uvicorn.run("web_server:web", host="0.0.0.0", port=int(config["EXTERNAL_PORT"]), reload=True)

if __name__ == "__main__":
    main() 