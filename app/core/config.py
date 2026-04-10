from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="forbid")

    database_url: str
    async_database_url: str
    engine_pool_size: int = 20
    engine_max_overflow: int = 10

    max_users_per_event: int = 10
    max_responses_per_user: int = 20
    max_tries_code_generation: int = 10

    log_level: str = "INFO"

    cors_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:5173"]


settings = Settings()  # type: ignore[call-arg]
