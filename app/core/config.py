from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Main Settings
    APP_NAME: str = "BlastSquad"
    DATABASE_URL: str
    DEBUG: bool = False
    # Other settings can be added here as needed


settings = Settings()