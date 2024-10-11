from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "slime"
    admin_email: str = "toki0327@naver.com"
    EXTERNAL_PORT: str  # 환경 변수와 매칭되는 변수
    YOUTUBE_API_KEY: str
    TOUR_API_KEY:str
    db_host: str
    db_user: str  # DB_USER에서 __를 제거하여 db_user로 변경
    db_password: str
    db_database: str
    db_port: int

    model_config = SettingsConfigDict(env_file=".env")

