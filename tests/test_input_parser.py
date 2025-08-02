import pytest
from app.input_parser import parse_input_type


class TestInputParser:
    
    def test_parse_latlon_valid(self):
        result = parse_input_type("35.6586, 139.7454")
        assert result == ('latlon', "35.6586, 139.7454")
    
    def test_parse_latlon_negative(self):
        result = parse_input_type("-35.6586, -139.7454")
        assert result == ('latlon', "-35.6586, -139.7454")
    
    def test_parse_latlon_with_spaces(self):
        result = parse_input_type("  35.6586  ,  139.7454  ")
        assert result == ('latlon', "  35.6586  ,  139.7454  ")
    
    def test_parse_suumo_url_now_invalid(self):
        url = "https://suumo.jp/chintai/tokyo/example"
        result = parse_input_type(url)
        assert result == ('invalid_url', url)
    
    def test_parse_suumo_url_jj_now_invalid(self):
        url = "https://suumo.jp/jj/example"
        result = parse_input_type(url)
        assert result == ('invalid_url', url)
    
    def test_parse_invalid_url(self):
        url = "https://example.com/test"
        result = parse_input_type(url)
        assert result == ('invalid_url', url)
    
    def test_parse_address(self):
        address = "東京都新宿区西新宿1-1-1"
        result = parse_input_type(address)
        assert result == ('address', address)
    
    def test_parse_address_japanese(self):
        address = "千代田区霞が関1-1-1"
        result = parse_input_type(address)
        assert result == ('address', address)
    
    def test_parse_invalid_latlon(self):
        result = parse_input_type("invalid, coordinates")
        assert result == ('address', "invalid, coordinates")
    
    def test_parse_empty_string(self):
        result = parse_input_type("")
        assert result == ('address', "")