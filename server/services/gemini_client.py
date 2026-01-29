
from google import genai
import os
from config import settings

class GeminiClient:
    def __init__(self):
        self.api_key = settings.google_api_key
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY not found in settings")
        self.client = genai.Client(api_key=self.api_key)
        # Use a model that is available - defaulting to 1.5 flash for speed/cost if 2.0 isn't available
        # But user tested with gemini-2.0-flash-exp (referenced as gemini-3-flash-preview in user script?)
        # Let's use a standard reliable model first.
        self.model = settings.model_name if hasattr(settings, 'model_name') else "gemini-2.0-flash-exp" 

    def generate(self, prompt: str) -> str:
        print(f"DEBUG: Sending request to Gemini ({self.model})...")
        try:
            # Add simple configuration for robustness
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
            print(f"ERROR: Gemini generation failed: {e}")
            raise e

gemini_client = GeminiClient()
