from requests import Response
from mock import patch
import pytest

from app import create_app
from swapi import SWApi

@pytest.fixture()
def app():
    app = create_app()
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_swapi_min_cargo_capacity_vehicles(client):
    url_to_test = "/swapi/vehicles"
    response = SWApi().get("/vehicles")
    total = response.json()["count"]
    
    with client.get(url_to_test) as res:
        assert res.status_code == 200
        assert len(res.json["available_vehicles"]) == total

    with client.get(url_to_test, query_string={"min_cargo_capacity": ""}) as res:
        assert res.status_code == 200
        assert len(res.json["available_vehicles"]) == total

    with client.get(url_to_test, query_string={"min_cargo_capacity": "a"}) as res:
        assert res.status_code == 400

    min_cargo_capacity = 50000
    with client.get(url_to_test, query_string={"min_cargo_capacity": min_cargo_capacity}) as res:
        assert res.status_code == 200
        for vehicle in res.json["available_vehicles"]:
            assert int(vehicle["cargo_capacity"]) >= min_cargo_capacity

    with patch('swapi.SWApi.get', side_effect=Exception("error")):
        with client.get(url_to_test) as res:
            assert res.status_code == 404

    with patch('swapi.SWApi.get') as mock_get:
        mock_response = Response()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
        with client.get(url_to_test) as res:
            assert res.status_code == 403
