from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    use_gemini: bool = False
    google_api_key: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
