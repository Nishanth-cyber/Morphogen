from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    use_gemini: bool = False
    gemini_model: str =  os.getenv("GEMINI_MODEL")
    google_api_key: str = os.getenv("GOOGLE_API_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
