from sqlmodel import Session, SQLModel, create_engine
from config import Settings

# Settings 인스턴스 생성
settings = Settings()

# MySQL connection string
DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_database}"
)

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)

# 데이터베이스 세션 생성기
def get_session():
    with Session(engine) as session:
        yield session
        
