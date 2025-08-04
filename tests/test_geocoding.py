import responses
from unittest.mock import patch
from app.geocoding import geocode, reverse_geocode, get_pref_code


class TestGeocoding:
    
    @responses.activate
    def test_geocode_success(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={
                "status": "OK",
                "results": [
                    {
                        "geometry": {
                            "location": {
                                "lat": 35.6586,
                                "lng": 139.7454
                            }
                        }
                    }
                ]
            },
            status=200
        )
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = geocode("東京都新宿区")
            assert result == (35.6586, 139.7454)
    
    @responses.activate
    def test_geocode_api_error(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "ZERO_RESULTS"},
            status=200
        )
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = geocode("無効な住所")
            assert result is None
    
    def test_geocode_no_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            result = geocode("東京都新宿区")
            assert result is None
    
    @responses.activate
    def test_reverse_geocode_success(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={
                "status": "OK",
                "results": [
                    {
                        "formatted_address": "東京都新宿区西新宿1-1-1"
                    }
                ]
            },
            status=200
        )
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = reverse_geocode(35.6586, 139.7454)
            assert result == "東京都新宿区西新宿1-1-1"
    
    @responses.activate
    def test_get_pref_code_tokyo(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={
                "status": "OK",
                "results": [
                    {
                        "formatted_address": "東京都新宿区西新宿1-1-1"
                    }
                ]
            },
            status=200
        )
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = get_pref_code(35.6586, 139.7454)
            assert result == "13"
    
    @responses.activate
    def test_get_pref_code_no_match(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={
                "status": "OK",
                "results": [
                    {
                        "formatted_address": "Some Foreign Address"
                    }
                ]
            },
            status=200
        )
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            result = get_pref_code(35.6586, 139.7454)
            assert result is None