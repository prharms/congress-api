from unittest.mock import patch, Mock
import requests

from congress_api.services.api_client import CongressApiClient


def make_response(status_code=200, json_payload=None):
    m = Mock()
    m.status_code = status_code
    def _json():
        if isinstance(json_payload, Exception):
            raise json_payload
        return json_payload
    m.json = _json
    return m


@patch("congress_api.services.api_client.time.sleep")
@patch("congress_api.services.api_client.requests.get")
def test_api_client_200(mock_get, mock_sleep):
    mock_get.return_value = make_response(200, {"ok": True})
    client = CongressApiClient(api_key="k")
    resp = client.get_member_votes(118, 1, 1)
    assert resp.status_code == 200
    assert resp.json == {"ok": True}


@patch("congress_api.services.api_client.time.sleep")
@patch("congress_api.services.api_client.requests.get")
def test_api_client_404(mock_get, mock_sleep):
    mock_get.return_value = make_response(404, {"error": "No Vote matches the given query"})
    client = CongressApiClient(api_key="k")
    resp = client.get_member_votes(118, 1, 99999)
    assert resp.status_code == 404


@patch("congress_api.services.api_client.time.sleep")
@patch("congress_api.services.api_client.requests.get")
def test_api_client_429_then_200(mock_get, mock_sleep):
    mock_get.side_effect = [
        make_response(429, {"retry": True}),
        make_response(200, {"ok": True}),
    ]
    client = CongressApiClient(api_key="k")
    resp = client.get_member_votes(118, 1, 1)
    assert resp.status_code == 200
    assert resp.json == {"ok": True}


@patch("congress_api.services.api_client.time.sleep")
@patch("congress_api.services.api_client.requests.get")
def test_api_client_bad_json(mock_get, mock_sleep):
    class BadJson(Exception):
        pass
    mock_get.return_value = make_response(200, BadJson("boom"))
    client = CongressApiClient(api_key="k")
    resp = client.get_member_votes(118, 1, 1)
    assert resp.status_code == 200
    assert resp.json is None


@patch("congress_api.services.api_client.time.sleep")
@patch("congress_api.services.api_client.requests.get")
def test_api_client_network_error(mock_get, mock_sleep):
    mock_get.side_effect = requests.RequestException("net")
    client = CongressApiClient(api_key="k")
    resp = client.get_member_votes(118, 1, 1)
    assert resp.status_code == 0
    assert resp.json is None


