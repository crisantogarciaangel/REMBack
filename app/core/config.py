from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_dsn: str
    mongo_uri: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
