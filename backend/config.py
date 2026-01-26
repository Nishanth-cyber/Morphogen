import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    MODEL_NAME = "gemini-pro"
    TEMPERATURE = 0.3  # Lower temperature for more consistent outputs
    MAX_TOKENS = 2000
    
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
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found. Please create a .env file with your API key.")
        
        # Create output directory if it doesn't exist
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
