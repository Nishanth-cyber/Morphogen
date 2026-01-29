
from google import genai
import os
from config import settings

class GeminiClient:
    def __init__(self):
        self.api_key = settings.google_api_key
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY not found in settings")
        self.client = genai.Client(api_key=self.api_key)
        self.model = settings.gemini_model 

    def generate(self, prompt: str) -> str:
        print(f"DEBUG: Sending request to Gemini ({self.model})...")
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.1
                    )
                )
                print("DEBUG: Received response from Gemini")
                return response.text
            except Exception as e:
                import time
                import random
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if attempt < max_retries - 1:
                        sleep_time = (base_delay * (2 ** attempt)) + (random.random() * 0.5)
                        print(f"WARNING: Rate limit hit (429). Retrying in {sleep_time:.2f} seconds... (Attempt {attempt+1}/{max_retries})")
                        print(f"Details: {error_str[:200]}...") # Log partial error for context
                        time.sleep(sleep_time)
                        continue
                
                print(f"ERROR: Gemini generation failed: {e}")
                raise e

gemini_client = GeminiClient()
