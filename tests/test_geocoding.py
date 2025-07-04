import pytest
from unittest.mock import patch, Mock
from src.app.geocoding import geocode, get_pref_code
import json

# geocodeのモックデータ
GEOCODE_SUCCESS_RESPONSE = {
    "results": [
        {
            "geometry": {
                "location": {
                    "lat": 35.6895,
                    "lng": 139.6917
                }
            }
        }
    ],
    "status": "OK"
}

GEOCODE_ZERO_RESULTS_RESPONSE = {
    "results": [],
    "status": "ZERO_RESULTS"
}

# get_pref_codeのモックデータ
PREF_CODE_SUCCESS_RESPONSE = {
    "results": [
        {
            "address_components": [
                {
                    "long_name": "東京都",
                    "types": ["administrative_area_level_1"]
                }
            ]
        }
    ],
    "status": "OK"
}

PREF_CODE_ZERO_RESULTS_RESPONSE = {
    "results": [],
    "status": "ZERO_RESULTS"
}

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get

def test_geocode_success(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, text=json.dumps(GEOCODE_SUCCESS_RESPONSE))
    lat, lon = geocode("東京都庁")
    assert lat == 35.6895
    assert lon == 139.6917

def test_geocode_failure(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, text=json.dumps(GEOCODE_ZERO_RESULTS_RESPONSE))
    lat, lon = geocode("存在しない住所")
    assert lat is None
    assert lon is None

def test_get_pref_code_success(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, text=json.dumps(PREF_CODE_SUCCESS_RESPONSE))
    pref_code = get_pref_code(35.6895, 139.6917)
    assert pref_code == "13"

def test_get_pref_code_failure(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, text=json.dumps(PREF_CODE_ZERO_RESULTS_RESPONSE))
    pref_code = get_pref_code(0.0, 0.0)
    assert pref_code == "00"
