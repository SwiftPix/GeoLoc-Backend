import requests
from settings import settings
from database.models import Currency
from utils.exceptions import CountryNotFound, CurrenciesNotFound, DesiredCurrencyNotFound, ExchangeApiError, GoogleMapsApiError, TaxNotFound

class GeoController:
    def get_country(self, latitude, longitude):
        url = f"{settings.GOOGLE_MAPS_API}?latlng={latitude},{longitude}&key={settings.GOOGLE_API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            raise GoogleMapsApiError("Geolocalização está indisponível")
        data = response.json()
        for address_component in data["results"][0]["address_components"]:
            if "country" in address_component["types"]:
                country_code = address_component["short_name"]
        return country_code
    
    def get_exchanges(self, currency):
        url = f"{settings.CURRENCY_API}/{settings.CURRENCY_API_KEY}/latest/{currency}"
        response = requests.get(url)
        if response.status_code != 200:
            raise ExchangeApiError("Taxas das moedas está indisponível")
        data = response.json()
        return data.get("conversion_rates", {})
    
    def get_conversion(self, base_currency, desired_currency, amount):
        url = f"{settings.CURRENCY_API}/{settings.CURRENCY_API_KEY}/pair/{base_currency}/{desired_currency}/{amount}"
        response = requests.get(url)
        if response.status_code != 200:
            raise ExchangeApiError("Taxas das moedas está indisponível")

        data = response.json()
        return data.get("conversion_result", {})
    
    def get_tax_by_coords(self, latitude, longitude, desired_currency):
        current_country = self.get_country(latitude, longitude)
        if not current_country:
            raise CountryNotFound("Não foi possível localizar o país com as coordenadas fornecidas")

        base_currency = Currency.find_by_country(current_country)
        if not base_currency:
            raise DesiredCurrencyNotFound("Moeda desejada não encontrada")
        tax = self.get_tax(base_currency, desired_currency)
        if not tax:
            raise TaxNotFound("Conversão para moeda desejada não encontrada")

        return tax
    
    def get_tax(self, current_currency, desired_currency):
        currencies = self.get_exchanges(current_currency)
        if not currencies:
            raise CurrenciesNotFound("Não foi possível buscar moedas para o país com as coordenadas fornecidas")
        
        if currencies.get(desired_currency):
            return currencies[desired_currency]
        return {}
    
    def get_conversion_by_country(self, sender_country, receiver_country, amount):
        base_currency = Currency.find_by_country(sender_country)
        if not base_currency:
            raise DesiredCurrencyNotFound("Moeda para país atual não encontrada")

        desired_currency = Currency.find_by_country(receiver_country)
        if not desired_currency:
            raise DesiredCurrencyNotFound("Moeda para país desejado não encontrada")
        
        conversion = self.get_conversion(base_currency, desired_currency, amount)

        if not conversion:
            raise TaxNotFound("Conversão para moeda desejada não encontrada")
        return conversion
    
    def get_currency_by_coords(self, latitude, longitude):
        current_country = self.get_country(latitude, longitude)
        if not current_country:
            raise CountryNotFound("Não foi possível localizar o país com as coordenadas fornecidas")

        currency = Currency.find_by_country(current_country)
        return currency
    
    def get_currencies(self):
        currencies = Currency.find()
        for currency in currencies:
            currency["_id"] = str(currency["_id"])
        return currencies
        
