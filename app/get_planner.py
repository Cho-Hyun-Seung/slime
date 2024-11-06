from sqlmodel import Session, select
from models import TouristSpot
from get_spots import get_nearby_tourist_spot


async def get_planner(map_x, map_y, settings, session: Session):
    # 1. 주변 관광지를 가져옴
    nearby_spots = await get_nearby_tourist_spot(map_x=map_x, map_y=map_y, settings=settings, num_of_rows=20)
    
    for place in nearby_spots:
        positive_rate = 0
        # 데이터베이스에서 관광지 정보를 가져옴
        spot_eval = session.exec(select(TouristSpot).where(TouristSpot.content_id == place["content_id"])).first()
        
        if spot_eval:
            place["negative"] = spot_eval.negative
            place["positive"] = spot_eval.positive
            place["total_review"] = spot_eval.total_review
            
            # 리뷰가 있을 경우에만 긍정 리뷰 비율 계산
            if place["total_review"] > 0:
                positive_rate = (place["positive"] / place["total_review"]) * 100
        
        distance = float(place["dist"])

        # 1순위: 긍정 리뷰 비율이 40% 이상이고, 거리 5km 이하
        if positive_rate >= 80 and distance <= 5000:
            place["rank"] = 1
        # 2순위: 긍정 리뷰 비율이 40% 이상이고, 거리 10km 이하
        elif positive_rate >= 60 and distance <= 5000:
            place["rank"] = 2
        elif positive_rate >= 40 and distance <= 10000:
            place["rank"] = 3
        # 3순위: 나머지
        else:
            place["rank"] = 4

    # rank 값과 dist 값을 기준으로 정렬
    sorted_places = sorted(nearby_spots, key=lambda x: (x["rank"], x["dist"]))
    # print(sorted_places)
    return sorted_places
