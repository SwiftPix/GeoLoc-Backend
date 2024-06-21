from flask import Blueprint, request, jsonify
from src.controllers.geoloc_controller import GeoController
from src.schemas import ConversionCountrySchema, ConversionSchema, TaxSchema
from src.utils.exceptions import CountryNotFound, CurrenciesNotFound, DesiredCurrencyNotFound, ExchangeApiError, GoogleMapsApiError, TaxNotFound

bp = Blueprint("geoloc", __name__)

@bp.route("/health", methods=["GET"])
def health_check():
    return {"status":"ok", "message":"Service is healthy"}

@bp.route("/tax_coords", methods=["POST"])
def get_tax_by_coords():
    try:
        payload = request.get_json()
        validated_payload = TaxSchema().load(payload)
        tax = GeoController.get_tax_by_coords(
            validated_payload["latitude"],
            validated_payload["longitude"],
            validated_payload["sender_currency"]
        )
        return {"tax": tax}
    except (GoogleMapsApiError, ExchangeApiError) as e:
        return jsonify({"status": 500, "message": str(e)}), 500
    except (CountryNotFound, CurrenciesNotFound, TaxNotFound) as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/conversion", methods=["POST"])
def get_conversion():
    try:
        payload = request.get_json()
        validated_payload = ConversionCountrySchema().load(payload)
        exchange_currency = GeoController.get_conversion(
            validated_payload["sender_currency"],
            validated_payload["receiver_currency"],
            validated_payload["value"]
        )
        if not exchange_currency:
            raise TaxNotFound("Conversão não encontrada")
        return {"result": exchange_currency}
    except ExchangeApiError as e:
        return jsonify({"status": 500, "message": str(e)}), 500
    except TaxNotFound as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400
    
@bp.route("/conversion_by_country", methods=["POST"])
def get_conversion_by_country():
    try:
        payload = request.get_json()
        validated_payload = ConversionSchema().load(payload)
        exchange_currency = GeoController.get_conversion_by_country(
            validated_payload["sender_country"],
            validated_payload["receiver_country"],
            validated_payload["value"]
        )
        if not exchange_currency:
            raise DesiredCurrencyNotFound("Conversão não encontrada")
        return {"result": exchange_currency}
    except (DesiredCurrencyNotFound, TaxNotFound) as e:
        return jsonify({"status": 404, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": str(e)}), 400