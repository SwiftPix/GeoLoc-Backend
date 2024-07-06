import pytest
from flask import Flask
from pymongo import MongoClient
from main import create_app
from settings import settings

@pytest.fixture
def app():
    """Fixture para criar uma instância do aplicativo Flask para os testes."""
    app = create_app()

    app.config["TESTING"] = True
    app.config["MONGO_DATABASE_URI"] = settings.MONGO_DATABASE_URI
    app.config["MONGO_DATABASE_NAME"] = settings.MONGO_DATABASE_NAME

    with app.app_context():
        client = MongoClient(app.config["MONGO_DATABASE_URI"])
        db = client[app.config["MONGO_DATABASE_NAME"]]
        db.users.delete_many({})

        yield app

        db.users.delete_many({})
        client.close()

@pytest.fixture
def client(app):
    """Fixture para criar um cliente de teste para o aplicativo Flask."""
    return app.test_client()
