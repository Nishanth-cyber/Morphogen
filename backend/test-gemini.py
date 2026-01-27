import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("MODEL_NAME"))

try:
    response = model.generate_content("Explain how AI works in a few words")
    print("\nResponse from Gemini:")
    print(response.text)
    print("\n✅ API connection successful!")
except Exception as e:
    print(f"\n❌ API Error: {e}")