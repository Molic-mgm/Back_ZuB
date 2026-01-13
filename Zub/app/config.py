from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str

    JWT_SECRET: str = "change_me"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60 * 24 * 30

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    TELEGRAM_REQUIRED_CHAT_ID: str = ""

    VK_CLIENT_ID: str = ""
    VK_CLIENT_SECRET: str = ""
    VK_REDIRECT_URI: str = ""
    VK_REQUIRED_GROUP_ID: str = ""

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin_change_me"
    ADMIN_SESSION_SECRET: str = "admin_session_secret_change_me"

    REDIS_URL: str = ""
    LEADERBOARD_CACHE_TTL_SEC: int = 60

settings = Settings()
