from sqlmodel import Session
from models import TouristSpot
import json
import os

def get_pona(session: Session):
    dic_path = r'C:\Users\toki1\Documents\OneDrive\바탕 화면\slime\spot_Data'
    json_files = os.listdir(dic_path)
    datas = []
    
    for file_name in json_files:
        if file_name.endswith('.json'):
            file_path = os.path.join(dic_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # data에서 각 항목을 추출
                for content_id, details in data.items():
                    spot_data = TouristSpot(
                        content_id=int(content_id),  # JSON 파일에서 content_id를 가져옴
                        total_review=details.get("Total_review_Count", 0),
                        positive=details.get("positive", 0),
                        negative=details.get("negative", 0)
                    )
                    datas.append(spot_data)  # TouristSpot 인스턴스를 추가
    
    # 데이터베이스에 삽입
    session.add_all(datas)
    session.commit()
    
    return datas  # 모든 TouristSpot 객체를 포함한 리스트 반환
