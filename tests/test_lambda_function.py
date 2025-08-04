from unittest.mock import patch
from lambda_function import get_formatted_hazard_data, get_hazard_response, lambda_handler


class TestLambdaFunction:
    
    @patch('lambda_function.input_parser.parse_input_type')
    @patch('lambda_function.geocoding.geocode')
    @patch('lambda_function.hazard_info.get_all_hazard_info')
    @patch('lambda_function.hazard_info.format_all_hazard_info_for_display')
    def test_get_formatted_hazard_data_address(self, mock_format, mock_get_hazard, mock_geocode, mock_parse):
        mock_parse.return_value = ('address', '東京都新宿区')
        mock_geocode.return_value = (35.6586, 139.7454)
        mock_get_hazard.return_value = {'flood': 'low'}
        mock_format.return_value = {'洪水': '低リスク'}
        
        error, data, info = get_formatted_hazard_data('東京都新宿区')
        
        assert error is None
        assert data == {'洪水': '低リスク'}
        assert info == '「東京都新宿区」周辺のハザード情報です。'
    
    @patch('lambda_function.input_parser.parse_input_type')
    def test_get_formatted_hazard_data_invalid_latlon(self, mock_parse):
        mock_parse.return_value = ('latlon', 'invalid,coords')
        
        error, data, info = get_formatted_hazard_data('invalid,coords')
        
        assert error == "緯度・経度の形式が正しくありません。例: 35.6586, 139.7454"
        assert data is None
    
    @patch('lambda_function.input_parser.parse_input_type')
    def test_get_formatted_hazard_data_invalid_url(self, mock_parse):
        mock_parse.return_value = ('invalid_url', 'https://example.com')
        
        error, data, info = get_formatted_hazard_data('https://example.com')
        
        assert error == "無効なURLです。住所または緯度経度を入力してください。"
        assert data is None
    
    @patch('lambda_function.get_formatted_hazard_data')
    def test_get_hazard_response_success(self, mock_get_data):
        mock_get_data.return_value = (None, {'洪水': '低リスク'}, '東京都新宿区周辺のハザード情報です。')
        
        result = get_hazard_response('東京都新宿区')
        
        expected = "東京都新宿区周辺のハザード情報です。\n--------------------\n【洪水】\n低リスク"
        assert result == expected
    
    @patch('lambda_function.get_formatted_hazard_data')
    def test_get_hazard_response_error(self, mock_get_data):
        mock_get_data.return_value = ("エラーメッセージ", None, "")
        
        result = get_hazard_response('invalid input')
        
        assert result == "エラーメッセージ"
    
    @patch('lambda_function.line_handler.handle_line_event')
    def test_lambda_handler_success(self, mock_handle):
        event = {
            'headers': {'x-line-signature': 'test_signature'},
            'body': 'test_body'
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        assert result['body'] == '"OK"'
        mock_handle.assert_called_once()
    
    def test_lambda_handler_missing_signature(self):
        event = {
            'headers': {},
            'body': 'test_body'
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 400
        assert result['body'] == '"Missing X-Line-Signature"'