import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Key for email generation
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Gmail credentials for email sending
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Location coordinates (latitude, longitude)
# Format: "26.9124,75.7873" from .env file
coords_string = os.getenv("LOCATION_COORDS", "40.7128,-74.0060")
lat, lon = map(float, coords_string.replace(" ", "").split(","))
LOCATION_COORDS = (lat, lon)
