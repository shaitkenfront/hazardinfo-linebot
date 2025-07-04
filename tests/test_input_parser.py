import pytest
from src.app.input_parser import parse_input_type

def test_parse_input_type_latlon():
    input_text = "35.6895,139.6917"
    input_type, value = parse_input_type(input_text)
    assert input_type == "latlon"
    assert value == "35.6895,139.6917"

def test_parse_input_type_suumo_url():
    input_text = "https://suumo.jp/chintai/tokyo/sc_shinjuku/jnc_00000000000000000000000000000000/"
    input_type, value = parse_input_type(input_text)
    assert input_type == "suumo_url"
    assert value == input_text

def test_parse_input_type_address():
    input_text = "東京都庁"
    input_type, value = parse_input_type(input_text)
    assert input_type == "address"
    assert value == input_text

def test_parse_input_type_invalid_url():
    input_text = "http://example.com/invalid_url"
    input_type, value = parse_input_type(input_text)
    assert input_type == "invalid_url"
    assert value == input_text

def test_parse_input_type_other_text():
    input_text = "こんにちは"
    input_type, value = parse_input_type(input_text)
    assert input_type == "address"
    assert value == input_text
