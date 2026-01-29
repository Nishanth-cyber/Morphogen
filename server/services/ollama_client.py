import requests
from config import settings
import os

# Import GeminiClient if available, or just use the file we created
try:
    from services.gemini_client import gemini_client as gemini_service
except ImportError:
    gemini_service = None

class LLMClient:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.use_gemini = settings.use_gemini

    def generate(self, prompt: str, format: str = None) -> str:
        if self.use_gemini:
            print("DEBUG: Using Gemini Backend")
            if not gemini_service:
                return "Error: Gemini service not available"
            return gemini_service.generate(prompt)

        # Fallback to Ollama
        print(f"DEBUG: Sending request to Ollama ({self.model})...")
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": -1,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.2
            }
        }
        if format:
            payload["format"] = format

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=600
        )
        print(f"DEBUG: Received response from Ollama (Status: {response.status_code})")
        response.raise_for_status()
        return response.json()["response"]

# Rename instance to keep compatibility with agents
ollama_client = LLMClient()
