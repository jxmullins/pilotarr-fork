from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App config"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

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
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    WEBHOOK_RATE_LIMIT_WINDOW_SECONDS: int = 60
    WEBHOOK_RATE_LIMIT_MAX_REQUESTS: int = 120
    ACCESS_TOKEN_EXPIRE_HOURS: int = 720  # 30 days

    # App Info
    APP_NAME: str = "Pilotarr"
    APP_VERSION: str = "1.0.0"

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        """MariaDB connexion url"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:  # noqa: N802
        """Normalized CORS origins list from comma-separated env value."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
