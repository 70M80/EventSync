from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str
    database_url: str
    async_database_url: str
    engine_pool_size: int = 5
    engine_max_overflow: int = 5
    command_timeout: int = 45
    statement_timeout: str = "60000"
    pool_recycle: int = 1800
    pool_timeout: int = 30

    max_users_per_event: int = 20
    max_responses_per_user: int = 10
    max_tries_code_generation: int = 10

    ping_interval: int = 30
    idle_timeout: int = 120
    max_connections_per_event: int = 20

    log_level: str = "INFO"

    cors_origins: list[str] = ["http://localhost:8000", "http://127.0.0.1:5173"]


settings = Settings()  # type: ignore[call-arg]
