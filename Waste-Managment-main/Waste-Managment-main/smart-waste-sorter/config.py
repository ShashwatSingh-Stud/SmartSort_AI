import os
from dotenv import load_dotenv

# Load variables from .env if it exists
load_dotenv()

class Config:
    # MongoDB
    MONGO_DB_NAME = os.getenv("DB_NAME", "smartsort_ai")
    MONGO_URI = os.getenv("MONGO_URI", f"mongodb://localhost:27017/{MONGO_DB_NAME}")
    
    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Flask Settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-12345")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))

    # App Constants
    WASTE_CATEGORIES = ['plastic', 'paper', 'metal', 'organic']
    CO2_PER_ITEM = 0.5  # kg
