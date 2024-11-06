from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Category(SQLModel, table=True):
    category_code:str = Field(default=None, primary_key=True)
    category_name:str = Field(default=None)
    parentCategoryCode:str|None = Field(default=None)
    
class Category_Closure(SQLModel, table=True):
    category_code_ancestor:str =Field(default=None, primary_key=True, foreign_key="category.category_code")
    category_code_descendant:str=Field(default=None, primary_key=True, foreign_key="category.category_code")
    
class Region(SQLModel, table=True):
    id:int = Field(default=None, primary_key=True)
    region:str = Field(default=None)
    parent_code:int = Field(default=None)
    sigungu_code:int|None = Field(default=None)
    
class TouristSpot(SQLModel, table=True):
    __tablename__ = "tourist_spot" 
    content_id: int = Field(primary_key=True)
    total_review: int
    positive: int
    negative: int