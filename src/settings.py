import os

class Settings:
    def __init__(self):
        self.ENVIROMENT = os.getenv("ENVIROMENT", "dev")
        self.MONGO_DATABASE_URI = os.getenv("MONGO_DATABASE_URI", "mongodb://localhost:27017")
        self.MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "geoloc-dev")
        self.GOOGLE_MAPS_API = os.getenv("GOOGLE_MAPS_API", "https://maps.googleapis.com/maps/api/geocode/json")
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "api_key")
        self.CURRENCY_API = os.getenv("CURRENCY_API" ,"https://v6.exchangerate-api.com/v6")
        self.CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY", "api_key")

settings = Settings()
