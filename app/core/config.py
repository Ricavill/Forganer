from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Friends Activity Planner"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/friends_activity_planner"

    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536

    bot_agent_history_limit: int = 20
    bot_agent_memory_top_k: int = 5

    mcp_server_url: str = "http://localhost:8765/mcp"
    bot_agent_max_tool_rounds: int = 4

    model_config = {"env_file": ".env"}


settings = Settings()
