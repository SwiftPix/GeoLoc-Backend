import pymongo

from bson.objectid import ObjectId
from settings import settings

db_client = pymongo.MongoClient(settings.MONGO_DATABASE_URI)
db = db_client.get_database(settings.MONGO_DATABASE_NAME)

class Currency:
    def __init__(self, currency, country_iso2, country):
        self.currency = currency
        self.country_iso2 = country_iso2
        self.country = country

    def save(self):
        currency = {
            "currency": self.currency,
            "country_iso2": self.country_iso2,
            "country": self.country
        }
        result = db.currency.insert_one(currency)
        return result.inserted_id
    
    def find():
        response = []
        result = db.currency.find({})
        for item in result:
            response.append(item)
        return response
    
    def find_by_id(currency_id):
        result = db.currency.find({"_id": ObjectId(currency_id)})
        currency = next(result, None)
        return currency
    
    def find_by_country(country):
        result = db.currency.find_one({"country_iso2": country})
        if result:
            return result["currency"]
        return {}