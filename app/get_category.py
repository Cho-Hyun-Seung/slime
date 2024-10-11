from sqlmodel import Session, select
from models import Category
from fastapi import HTTPException

# 카테고리 코드로 카테고리 가져오기
def get_category_by_code(session:Session, code: str) -> Category:
    # 주어진 코드로 카테고리를 데이터베이스에서 검색
    category = session.exec(select(Category).where(Category.category_code == code)).first()
    # 카테고리가 존재하지 않을 경우 404 오류 발생
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# 루트 카테고리 가져오기
def get_root_category(session:Session) -> list[Category]:
    # 부모 카테고리가 없는 루트 카테고리들을 데이터베이스에서 검색
    roots = session.exec(select(Category).where(Category.parentCategoryCode.is_(None))).all()
    return roots

# 특정 카테고리의 하위 카테고리 가져오기
def get_descendants_category(session:Session, parent_code: str) -> list[Category]:
    # 주어진 부모 카테고리 코드로 부모 카테고리를 데이터베이스에서 검색
    descendants_category = session.exec(select(Category).where(Category.parentCategoryCode == parent_code)).all()
    # 부모 카테고리가 존재하지 않을 경우 404 오류 발생
    if not descendants_category:
        raise HTTPException(status_code=404, detail="Parent category not found")
    
    # 부모 카테고리의 하위 카테고리들을 가져옴
    # descendants = parent_category.children
    return descendants_category
