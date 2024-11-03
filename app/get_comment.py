from googleapiclient.discovery import build
from fastapi import Depends, HTTPException
from config import Settings
import pandas as pd
import re  # 정규표현식 라이브러리
import os  # 운영 체제 기능을 위한 라이브러리

# 한글만 남기는 함수
def extract_korean(text):
    return re.sub(r"[^가-힣 ]", "", text)

def get_youtube_comments(video_id: str, settings: Settings = Depends(Settings)):
    api_key = settings.YOUTUBE_API_KEY

    # API 클라이언트 초기화
    try:
        api_obj = build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize YouTube API client: {str(e)}")
    video_title = ''
    comments = []

    try:
        video_response = api_obj.videos().list(part='snippet', id=video_id).execute()
        video_title = video_response['items'][0]['snippet']['title']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"영상 제목 가져오기 오류: {str(e)}")


    try:
        # 댓글을 YouTube API로부터 가져옴
        response = api_obj.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=100
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching comments: {str(e)}")
    while response:
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            # 한글만 추출하여 저장 (빈 문자열이 아닌 경우만 추가)
            korean_comment = extract_korean(comment['textDisplay']).strip()
            if korean_comment:  # 빈 문자열이 아닐 경우에만 추가
                comments.append({
                    'comment': korean_comment,
                    'label':''
                })

            # 답글이 있는 경우 처리
            if item['snippet']['totalReplyCount'] > 0:
                for reply_item in item['replies']['comments']:
                    reply = reply_item['snippet']
                    korean_reply = extract_korean(reply['textDisplay']).strip()
                    if korean_reply:  # 빈 문자열이 아닐 경우에만 추가
                        comments.append({
                            'comment': korean_reply,
                                                'label':''
                        })

        # 다음 페이지의 댓글 가져오기
        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100
            ).execute()
        else:
            break

    # 댓글을 DataFrame으로 변환
    if comments:  # 비어있지 않을 때만 파일 저장
        df = pd.DataFrame(comments)
        
        # directory = 'commentCSV'
        # if not os.path.exists(directory):
        #     os.makedirs(directory)  # 디렉터리가 없으면 생성
        
        # 파일 경로 설정
        file_path = os.path.join('commentCSV', f'{video_id}_comments.xlsx')
        
        # 엑셀 파일로 저장
        df.to_excel(file_path, index=False, header=True)

    return comments
