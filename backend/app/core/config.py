from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App config"""

    # Database
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    API_KEY: str
    WEBHOOK_SECRET: str = ""
    ACCESS_TOKEN_EXPIRE_HOURS: int = 720  # 30 days

    # App Info
    APP_NAME: str = "Pilotarr"
    APP_VERSION: str = "1.0.0"

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        """MariaDB connexion url"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
