from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    app_env: str = "development"
    
    # JWT Settings
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)  # Generate a random key if not set
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Policy
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_SPECIAL: bool = False
    
    # Rate Limiting
    LOGIN_RATE_LIMIT: int = 5  # attempts per window
    LOGIN_RATE_WINDOW: int = 900  # 15 minutes in seconds

    class Config:
        env_file = ".env"


settings = Settings()
