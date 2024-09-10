from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "slime"
    admin_email: str = "toki0327@naver.com"
    EXTERNAL_PORT: str  # 환경 변수와 매칭되는 변수

    model_config = SettingsConfigDict(env_file=".env")

