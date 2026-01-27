import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Choose AI Backend
    USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
    
    # Ollama Configuration (FREE - via Docker)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Google Gemini Configuration (requires billing account)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    
    # Application Configuration
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5000
    DEBUG = True
    
    # Output Configuration
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
    
    # Default Building Parameters
    DEFAULTS = {
        "residential": {
            "wall_thickness": 230,  # mm
            "door_width": 900,      # mm
            "window_width": 1200,   # mm
            "min_room_area": {
                "living_room": 150,  # sq.ft
                "bedroom": 100,
                "kitchen": 80,
                "bathroom": 25
            }
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        
        if cls.USE_OLLAMA:
            print("=" * 60)
            print("🐳 Using Ollama (FREE Local AI via Docker)")
            print("=" * 60)
            print(f"   Base URL: {cls.OLLAMA_BASE_URL}")
            print(f"   Model: {cls.OLLAMA_MODEL}")
            print("=" * 60)
        else:
            print("=" * 60)
            print("☁️ Using Google Gemini (Cloud AI)")
            print("=" * 60)
            if not cls.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not found. Please set USE_OLLAMA=true or provide API key.")
            print(f"   Model: {cls.MODEL_NAME}")
            print("=" * 60)
        
        # Create output directory if it doesn't exist
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
