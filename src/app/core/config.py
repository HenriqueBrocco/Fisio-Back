from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_name: str = "fisio-api"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()