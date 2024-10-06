from googleapiclient.discovery import build
from fastapi import Depends
from config import Settings
import pandas as pd  # Pandas 라이브러리 import

def get_youtube_comments(video_id: str, settings: Settings = Depends(Settings)):
    api_key = settings.YOUTUBE_API_KEY

    # API 클라이언트 초기화
    api_obj = build('youtube', 'v3', developerKey=api_key)

    comments = []

    # 댓글을 YouTube API로부터 가져옴
    response = api_obj.commentThreads().list(
        part='snippet,replies',
        videoId=video_id,
        maxResults=100
    ).execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'comment': comment['textDisplay'],
                'author': comment['authorDisplayName'],
                'date': comment['publishedAt'],
                'num_likes': comment['likeCount']
            })

            if item['snippet']['totalReplyCount'] > 0:
                for reply_item in item['replies']['comments']:
                    reply = reply_item['snippet']
                    comments.append({
                        'comment': reply['textDisplay'],
                        'author': reply['authorDisplayName'],
                        'date': reply['publishedAt'],
                        'num_likes': reply['likeCount']
                    })

        # 다음 페이지 댓글 가져오기
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
    df = pd.DataFrame(comments)
    # 엑셀 파일로 저장
    df.to_excel(f'{video_id}_comments.xlsx', index=False, header=True)

    return comments
