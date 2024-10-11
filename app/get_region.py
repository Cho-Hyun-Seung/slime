from fastapi import HTTPException
from sqlmodel import Session, select
from models import Region


def get_root_regions(session:Session) -> list[Region]:
    root_regions = session.exec(select(Region).where(Region.parentId.is_(None))).all()
    return root_regions

def get_child_regions(session:Session, parent_region) ->list[Region]:
    parent_region = session.exec(select(Region).where(Region.region == parent_region)).first()
    if parent_region is None:
        raise HTTPException(status_code=404, detail="모지역이 없습니다!")
    
    child_regions = session.exec(select(Region).where(Region.parentId == parent_region.id)).all()
    return child_regions