from copy import deepcopy
import json
from utils.exceptions import ExchangeApiError, GoogleMapsApiError
from tests.payloads import payload_tax, payload_conversion, payload_conversion_by_country, payload_coords



def test_tax_coords_success(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com sucesso."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = "BR"

    mock_exchange = mocker.patch("controllers.geoloc_controller.GeoController.get_exchanges")

    mock_exchange.return_value = {"USD": 3.50}

    response = client.post("/tax_coords", json=payload_tax)

    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["tax"] == 3.50


def test_tax_coords_google_error(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com erro na api da localização."""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_country", side_effect=GoogleMapsApiError("Geolocalização está indisponível")
    )

    response = client.post("/tax_coords", json=payload_tax)

    assert response.status_code == 500
    assert response.json == {"status": 500, "message": "Geolocalização está indisponível"}


def test_tax_coords_exchange_error(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com erro na api de conversão."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = "BR"

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_exchanges", side_effect=ExchangeApiError("Taxas das moedas está indisponível")
    )

    response = client.post("/tax_coords", json=payload_tax)

    assert response.status_code == 500
    assert response.json == {"status": 500, "message": "Taxas das moedas está indisponível"}


def test_tax_coords_country_not_found(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com país não encontrado."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = {}

    response = client.post("/tax_coords", json=payload_tax)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Não foi possível localizar o país com as coordenadas fornecidas"}


def test_tax_coords_currency_not_found(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com conversões não encontradas."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = "BR"

    mock_exchange = mocker.patch("controllers.geoloc_controller.GeoController.get_exchanges")

    mock_exchange.return_value = {}

    response = client.post("/tax_coords", json=payload_tax)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Não foi possível buscar moedas para o país com as coordenadas fornecidas"}


def test_tax_coords_tax_not_found(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com taxa de câmbio não encontrada."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = "BR"

    mock_exchange = mocker.patch("controllers.geoloc_controller.GeoController.get_exchanges")

    mock_exchange.return_value = {"CAD": 4.5}

    response = client.post("/tax_coords", json=payload_tax)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Conversão para moeda desejada não encontrada"}


def test_tax_coords_desired_currency_not_found(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com moeda desejada não encontrada."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = "NonEC"

    response = client.post("/tax_coords", json=payload_tax)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Moeda desejada não encontrada"}


def test_tax_coords_invalid_payload(client):
    """Testa o endpoint de buscar taxa de câmbio payload inválido."""

    payload_tax_invalid = deepcopy(payload_tax)
    payload_tax_invalid.pop("sender_currency")

    response = client.post("/tax_coords", json=payload_tax_invalid)

    assert response.status_code == 422
    assert response.json == {"status": 422, "message": "{'sender_currency': ['A moeda desejada é obrigatória']}"}


def test_tax_coords_generic_error(client, mocker):
    """Testa o endpoint de buscar taxa de câmbio com erro generico."""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_tax_by_coords", side_effect=Exception("Erro generico")
    )

    response = client.post("/tax_coords", json=payload_tax)

    assert response.status_code == 400

def test_get_currencies(client, mocker):
    """Testa o endpoint de buscar moedas com sucesso."""

    response = client.get("/currencies")

    assert response.status_code == 200


def test_get_currencies_not_found(client, mocker):
    """Testa o endpoint de buscar moedas com moedas não encontradas."""

    mock_currencies = mocker.patch("controllers.geoloc_controller.GeoController.get_currencies")
    
    mock_currencies.return_value = {}

    response = client.get("/currencies")

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Não foi possível buscar as moedas"}


def test_get_currencies_generic_error(client, mocker):
    """Testa o endpoint de buscar moedas com erro generico."""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_currencies", side_effect=Exception("Erro generico")
    )

    response = client.get("/currencies")

    assert response.status_code == 400


def test_conversion_success(client, mocker):
    """Testa o endpoint de conversão com sucesso."""

    mock_conversion = mocker.patch("controllers.geoloc_controller.GeoController.get_conversion")
    
    mock_conversion.return_value = 45.0

    response = client.post("/conversion", json=payload_conversion)

    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["result"] == 45.0


def test_conversion_invalid_payload(client, mocker):
    """Testa o endpoint de conversão com payload inválido."""

    payload_conversion_invalid = deepcopy(payload_conversion)
    payload_conversion_invalid.pop("value")

    response = client.post("/conversion", json=payload_conversion_invalid)

    assert response.status_code == 422
    assert response.json == {"status": 422, "message": "{'value': ['O valor a ser convertido é obrigatório']}"}


def test_conversion_exchange_error(client, mocker):
    """Testa o endpoint de conversão com erro na api de conversão."""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_conversion", side_effect=ExchangeApiError("Taxas das moedas está indisponível")
    )

    response = client.post("/conversion", json=payload_conversion)

    assert response.status_code == 500
    assert response.json == {"status": 500, "message": "Taxas das moedas está indisponível"}


def test_conversion_generic_error(client, mocker):
    """Testa o endpoint de conversão com erro generico."""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_conversion", side_effect=Exception("Erro generico")
    )

    response = client.post("/conversion", json=payload_conversion)

    assert response.status_code == 400


def test_conversion_tax_not_found(client, mocker):
    """Testa o endpoint de conversion com taxa de câmbio não encontrada."""

    mock_conversion = mocker.patch("controllers.geoloc_controller.GeoController.get_conversion")
    
    mock_conversion.return_value = {}

    response = client.post("/conversion", json=payload_conversion)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Conversão não encontrada"}


def test_conversion_by_country_success(client, mocker):
    """Testa o endpoint de conversão por país com sucesso."""

    mock_conversion = mocker.patch("controllers.geoloc_controller.GeoController.get_conversion")
    
    mock_conversion.return_value = 45.0

    response = client.post("/conversion_by_country", json=payload_conversion_by_country)

    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["result"] == 45.0


def test_conversion_by_country_invalid_payload(client, mocker):
    """Testa o endpoint de conversão por país com payload inválido."""

    payload_conversion_by_country_invalid = deepcopy(payload_conversion_by_country)
    payload_conversion_by_country_invalid.pop("value")

    response = client.post("/conversion_by_country", json=payload_conversion_by_country_invalid)

    assert response.status_code == 422
    assert response.json == {"status": 422, "message": "{'value': ['O valor a ser convertido é obrigatório']}"}


def test_conversion_by_country_tax_not_found(client, mocker):
    """Testa o endpoint de conversion por país com taxa de câmbio não encontrada."""

    mock_conversion = mocker.patch("controllers.geoloc_controller.GeoController.get_conversion")
    
    mock_conversion.return_value = {}

    response = client.post("/conversion_by_country", json=payload_conversion_by_country)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Conversão para moeda desejada não encontrada"}


def test_conversion_by_country_generic_error(client, mocker):
    """Testa o endpoint de conversão por país com erro generico."""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_conversion_by_country", side_effect=Exception("Erro generico")
    )

    response = client.post("/conversion_by_country", json=payload_conversion_by_country)

    assert response.status_code == 400


def test_conversion_by_country_currency_not_found(client, mocker):
    """Testa o endpoint de conversão por país com moeda desejada não encontrada."""

    mock_find_by_country = mocker.patch("database.models.Currency.find_by_country")
    
    mock_find_by_country.return_value = {}

    response = client.post("/conversion_by_country", json=payload_conversion_by_country)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Moeda para país atual não encontrada"}


def test_currency_by_coords_success(client, mocker):
    """Testa o endpoint de busca de moeda por coordenadas com sucesso."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = "BR"

    response = client.post("/coords/currency", json=payload_coords)

    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["currency"] == "BRL"


def test_currency_by_coords_invalid_payload(client, mocker):
    """Testa o endpoint de busca de moeda por coordenadas com payload inválido."""

    payload_coords_invalid = deepcopy(payload_coords)
    payload_coords_invalid.pop("longitude")

    response = client.post("/coords/currency", json=payload_coords_invalid)

    assert response.status_code == 422
    assert response.json == {"status": 422, "message": "{'longitude': ['A longitude é obrigatória']}"}


def test_currency_by_coords_generic_error(client, mocker):
    """Testa o endpoint de busca de moeda por coordenadas com erro generico."""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_currency_by_coords", side_effect=Exception("Erro generico")
    )

    response = client.post("/coords/currency", json=payload_coords)

    assert response.status_code == 400


def test_currency_by_coords_google_error(client, mocker):
    """Testa o endpoint de busca de moeda por coordenadas com erro na api de geolocalização"""

    mocker.patch(
        "controllers.geoloc_controller.GeoController.get_country", side_effect=GoogleMapsApiError("Geolocalização está indisponível")
    )

    response = client.post("/coords/currency", json=payload_coords)

    assert response.status_code == 500
    assert response.json == {"status": 500, "message": "Geolocalização está indisponível"}


def test_currency_by_coords_currency_not_found(client, mocker):
    """Testa o endpoint de busca de moeda por coordenadas com moeda não encontrada."""

    mock_google_coords = mocker.patch("controllers.geoloc_controller.GeoController.get_country")
    
    mock_google_coords.return_value = {}

    response = client.post("/coords/currency", json=payload_coords)

    assert response.status_code == 404
    assert response.json == {"status": 404, "message": "Não foi possível localizar o país com as coordenadas fornecidas"}
