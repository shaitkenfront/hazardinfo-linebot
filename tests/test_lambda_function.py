import pytest
from unittest.mock import patch, Mock
from lambda_function import get_formatted_hazard_data, get_hazard_response

# モックデータ
MOCK_LATLON_INPUT = ("latlon", "35.0,135.0")
MOCK_SUUMO_URL_INPUT = ("suumo_url", "http://example.com/suumo")
MOCK_ADDRESS_INPUT = ("address", "東京都")
MOCK_INVALID_URL_INPUT = ("invalid_url", "http://invalid.com")

MOCK_GEOCODED_LATLON = (35.0, 135.0)
MOCK_SUUMO_ADDRESS = "東京都港区六本木"

MOCK_RAW_HAZARDS = {
    'jshis_prob_50': {'max_prob': 0.1, 'center_prob': 0.05},
    'inundation_depth': {'max_info': '5m以上', 'center_info': '3m以上'},
    'property_address': '東京都港区六本木' # SUUMOの場合のみ
}

MOCK_FORMATTED_HAZARDS = {
    '30年以内に震度5強以上の地震が起こる確率': '周辺100mの最大: 10%\n中心点: 5%',
    '想定最大浸水深': '周辺100mの最大: 5m以上\n中心点: 3m以上',
    '物件住所': '東京都港区六本木'
}

@pytest.fixture
def mock_dependencies():
    with patch('src.app.input_parser.parse_input_type') as mock_parse_input_type,
         patch('src.app.suumo_scraper.extract_address_from_suumo') as mock_extract_address_from_suumo,
         patch('src.app.geocoding.geocode') as mock_geocode,
         patch('src.app.hazard_info.get_all_hazard_info') as mock_get_all_hazard_info,
         patch('src.app.hazard_info.format_all_hazard_info_for_display') as mock_format_all_hazard_info_for_display:
        yield {
            "parse_input_type": mock_parse_input_type,
            "extract_address_from_suumo": mock_extract_address_from_suumo,
            "geocode": mock_geocode,
            "get_all_hazard_info": mock_get_all_hazard_info,
            "format_all_hazard_info_for_display": mock_format_all_hazard_info_for_display,
        }

def test_get_formatted_hazard_data_latlon(mock_dependencies):
    mock_dependencies["parse_input_type"].return_value = MOCK_LATLON_INPUT
    mock_dependencies["geocode"].return_value = MOCK_GEOCODED_LATLON
    mock_dependencies["get_all_hazard_info"].return_value = MOCK_RAW_HAZARDS
    mock_dependencies["format_all_hazard_info_for_display"].return_value = MOCK_FORMATTED_HAZARDS

    error_message, formatted_hazards, initial_greeting = get_formatted_hazard_data(MOCK_LATLON_INPUT[1])

    assert error_message is None
    assert formatted_hazards == MOCK_FORMATTED_HAZARDS
    assert initial_greeting == f"指定された座標（{MOCK_GEOCODED_LATLON[0]}, {MOCK_GEOCODED_LATLON[1]}）周辺のハザード情報です。"

def test_get_formatted_hazard_data_suumo_url(mock_dependencies):
    mock_dependencies["parse_input_type"].return_value = MOCK_SUUMO_URL_INPUT
    mock_dependencies["extract_address_from_suumo"].return_value = MOCK_SUUMO_ADDRESS
    mock_dependencies["geocode"].return_value = MOCK_GEOCODED_LATLON
    mock_dependencies["get_all_hazard_info"].return_value = MOCK_RAW_HAZARDS
    mock_dependencies["format_all_hazard_info_for_display"].return_value = MOCK_FORMATTED_HAZARDS

    error_message, formatted_hazards, initial_greeting = get_formatted_hazard_data(MOCK_SUUMO_URL_INPUT[1])

    assert error_message is None
    assert formatted_hazards == MOCK_FORMATTED_HAZARDS
    assert initial_greeting == f"SUUMO物件のハザード情報です。"
    assert mock_dependencies["get_all_hazard_info"].call_args[0][0] == MOCK_GEOCODED_LATLON[0] # lat
    assert mock_dependencies["get_all_hazard_info"].call_args[0][1] == MOCK_GEOCODED_LATLON[1] # lon
    assert mock_dependencies["get_all_hazard_info"].return_value['property_address'] == MOCK_SUUMO_ADDRESS

def test_get_formatted_hazard_data_address(mock_dependencies):
    mock_dependencies["parse_input_type"].return_value = MOCK_ADDRESS_INPUT
    mock_dependencies["geocode"].return_value = MOCK_GEOCODED_LATLON
    mock_dependencies["get_all_hazard_info"].return_value = MOCK_RAW_HAZARDS
    mock_dependencies["format_all_hazard_info_for_display"].return_value = MOCK_FORMATTED_HAZARDS

    error_message, formatted_hazards, initial_greeting = get_formatted_hazard_data(MOCK_ADDRESS_INPUT[1])

    assert error_message is None
    assert formatted_hazards == MOCK_FORMATTED_HAZARDS
    assert initial_greeting == f"「{MOCK_ADDRESS_INPUT[1]}」周辺のハザード情報です。"

def test_get_formatted_hazard_data_invalid_input(mock_dependencies):
    mock_dependencies["parse_input_type"].return_value = MOCK_INVALID_URL_INPUT

    error_message, formatted_hazards, initial_greeting = get_formatted_hazard_data(MOCK_INVALID_URL_INPUT[1])

    assert error_message == "無効なURLです。SUUMOの物件詳細ページのURLを入力してください。"
    assert formatted_hazards is None
    assert initial_greeting == ""

def test_get_hazard_response_success(mock_dependencies):
    mock_dependencies["parse_input_type"].return_value = MOCK_ADDRESS_INPUT
    mock_dependencies["geocode"].return_value = MOCK_GEOCODED_LATLON
    mock_dependencies["get_all_hazard_info"].return_value = MOCK_RAW_HAZARDS
    mock_dependencies["format_all_hazard_info_for_display"].return_value = MOCK_FORMATTED_HAZARDS

    expected_response = (
        f"「{MOCK_ADDRESS_INPUT[1]}」周辺のハザード情報です。\n" +
        "--------------------\n" +
        f"【30年以内に震度5強以上の地震が起こる確率】\n{MOCK_FORMATTED_HAZARDS['30年以内に震度5強以上の地震が起こる確率']}\n" +
        f"【想定最大浸水深】\n{MOCK_FORMATTED_HAZARDS['想定最大浸水深']}\n" +
        f"【物件住所】\n{MOCK_FORMATTED_HAZARDS['物件住所']}"
    )

    response = get_hazard_response(MOCK_ADDRESS_INPUT[1])
    assert response == expected_response

def test_get_hazard_response_error(mock_dependencies):
    mock_dependencies["parse_input_type"].return_value = MOCK_INVALID_URL_INPUT

    expected_response = "無効なURLです。SUUMOの物件詳細ページのURLを入力してください。"

    response = get_hazard_response(MOCK_INVALID_URL_INPUT[1])
    assert response == expected_response
