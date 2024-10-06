# Python 3.10 기반
FROM python:3.10

# 컨테이너의 작업 디렉토리 설정
WORKDIR /code

# requirements.txt와 src 디렉토리를 복사
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# # 가상 환경 생성
# RUN python3 -m venv venv

# # 가상 환경 활성화 및 패키지 설치
# RUN ./venv/bin/pip install --no-cache-dir --upgrade -r /code/requirements.txt

# # 환경 변수 설정
# ENV EXTERNAL_PORT=8000

# # start.sh 실행
# CMD ["/bin/bash", "start.sh"]
