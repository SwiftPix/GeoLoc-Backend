import bcrypt
import pymongo

from bson.objectid import ObjectId
from settings import settings
from utils.index import default_datetime

db_client = pymongo.MongoClient(settings.MONGO_DATABASE_URI)
db = db_client.get_database(settings.MONGO_DATABASE_NAME)

class Currency:
    def __init__(self, currency, country):
        self.currency = currency
        self.country = country

    def save(self):
        currency = {
            "currency": self.currency,
            "country": self.country
        }
        result = db.currency.insert_one(currency)
        return result.inserted_id
    
    def find():
        result = db.currency.find({})
        return result
    
    def find_by_id(currency_id):
        result = db.currency.find({"_id": ObjectId(currency_id)})
        currency = next(result, None)
        return currency
    
    def find_by_country(country):
        result = db.currency.find_one({"country": country})
        for item in result:
            currency = item["currency"]
        return currency