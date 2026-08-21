from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_base_url: str = "http://localhost:8000"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8765

    model_config = {"env_file": ".env"}


settings = Settings()
