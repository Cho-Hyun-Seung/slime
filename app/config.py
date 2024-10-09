from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "slime"
    admin_email: str = "toki0327@naver.com"
    EXTERNAL_PORT: str  # 환경 변수와 매칭되는 변수
    YOUTUBE_API_KEY: str
    TOUR_API_KEY:str

    model_config = SettingsConfigDict(env_file=".env")

