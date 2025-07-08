import pytest
import json
import responses
from unittest.mock import patch, MagicMock
from hazard_api_function import lambda_handler, validate_coordinates, get_hazard_from_input


class TestHazardAPI:
    
    def test_validate_coordinates_valid(self):
        """有効な緯度経度のテスト"""
        is_valid, error = validate_coordinates(35.6586, 139.7454)
        assert is_valid is True
        assert error is None
    
    def test_validate_coordinates_invalid_lat(self):
        """無効な緯度のテスト"""
        is_valid, error = validate_coordinates(50.0, 139.7454)
        assert is_valid is False
        assert "緯度は24.0〜46.0の範囲" in error
    
    def test_validate_coordinates_invalid_lon(self):
        """無効な経度のテスト"""
        is_valid, error = validate_coordinates(35.6586, 150.0)
        assert is_valid is False
        assert "経度は123.0〜146.0の範囲" in error
    
    def test_validate_coordinates_non_numeric(self):
        """数値以外の入力のテスト"""
        is_valid, error = validate_coordinates("abc", "def")
        assert is_valid is False
        assert "数値で入力してください" in error
    
    def test_options_request(self):
        """OPTIONSリクエスト（プリフライト）のテスト"""
        event = {
            'httpMethod': 'OPTIONS'
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']
        assert result['headers']['Access-Control-Allow-Origin'] == '*'
    
    def test_get_request_missing_params(self):
        """GETリクエストで必須パラメータが不足しているテスト"""
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {}
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['error'] == 'Missing parameters'
    
    def test_get_request_invalid_coords(self):
        """GETリクエストで無効な座標のテスト"""
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {
                'lat': '50.0',
                'lon': '139.7454'
            }
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['error'] == 'Invalid coordinates'
    
    def test_post_request_invalid_json(self):
        """POSTリクエストで無効なJSONのテスト"""
        event = {
            'httpMethod': 'POST',
            'body': 'invalid json'
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['error'] == 'Invalid JSON'
    
    def test_post_request_missing_params(self):
        """POSTリクエストで必須パラメータが不足しているテスト"""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'lat': 35.6586})
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['error'] == 'Missing parameters'
    
    def test_unsupported_method(self):
        """サポートされていないHTTPメソッドのテスト"""
        event = {
            'httpMethod': 'DELETE'
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 405
        body = json.loads(result['body'])
        assert body['error'] == 'Method not allowed'
    
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    def test_get_request_success(self, mock_get_hazard):
        """GETリクエストの成功テスト"""
        # モックデータの設定
        mock_hazard_data = {
            'jshis_prob_50': {'max_prob': 0.85, 'center_prob': 0.80},
            'inundation_depth': {'max_info': '3m以上5m未満', 'center_info': '0.5m以上3m未満'}
        }
        mock_get_hazard.return_value = mock_hazard_data
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {
                'lat': '35.6586',
                'lon': '139.7454'
            }
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'success'
        assert body['coordinates']['latitude'] == 35.6586
        assert body['coordinates']['longitude'] == 139.7454
        assert body['hazard_info'] == mock_hazard_data
        
        # ハザード情報取得関数が正しい引数で呼ばれたか確認
        mock_get_hazard.assert_called_once_with(35.6586, 139.7454)
    
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    def test_post_request_success(self, mock_get_hazard):
        """POSTリクエストの成功テスト"""
        # モックデータの設定
        mock_hazard_data = {
            'jshis_prob_60': {'max_prob': 0.15, 'center_prob': 0.12},
            'tsunami_inundation': {'max_info': '浸水想定なし', 'center_info': '浸水想定なし'}
        }
        mock_get_hazard.return_value = mock_hazard_data
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'lat': 35.6586,
                'lon': 139.7454
            })
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'success'
        assert body['coordinates']['latitude'] == 35.6586
        assert body['coordinates']['longitude'] == 139.7454
        assert body['hazard_info'] == mock_hazard_data
        
        # ハザード情報取得関数が正しい引数で呼ばれたか確認
        mock_get_hazard.assert_called_once_with(35.6586, 139.7454)
    
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    def test_api_error_handling(self, mock_get_hazard):
        """API内部エラーのテスト"""
        # ハザード情報取得でエラーが発生する場合
        mock_get_hazard.side_effect = Exception("Test error")
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {
                'lat': '35.6586',
                'lon': '139.7454'
            }
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['error'] == 'Internal server error'
        assert 'Test error' in body['message']
    
    def test_cors_headers_present(self):
        """CORSヘッダーが正しく設定されているかテスト"""
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {}
        }
        
        result = lambda_handler(event, None)
        
        headers = result['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert 'Access-Control-Allow-Headers' in headers
        assert 'Access-Control-Allow-Methods' in headers
        assert headers['Content-Type'] == 'application/json'
    
    # 新しい住所解析機能のテスト
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    @patch('hazard_api_function.geocoding.geocode')
    def test_get_hazard_from_input_address(self, mock_geocode, mock_get_hazard):
        """住所からハザード情報取得のテスト"""
        # モックの設定
        mock_geocode.return_value = (35.6586, 139.7454)
        mock_hazard_data = {
            'jshis_prob_50': {'max_prob': 0.85, 'center_prob': 0.80}
        }
        mock_get_hazard.return_value = mock_hazard_data
        
        result = get_hazard_from_input("東京都新宿区")
        
        assert result['status'] == 'success'
        assert result['input_type'] == 'address'
        assert result['source'] == '住所: 東京都新宿区'
        assert result['coordinates']['latitude'] == 35.6586
        assert result['coordinates']['longitude'] == 139.7454
        assert result['hazard_info'] == mock_hazard_data
        
        mock_geocode.assert_called_once_with('東京都新宿区')
        mock_get_hazard.assert_called_once_with(35.6586, 139.7454)
    
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    def test_get_hazard_from_input_coordinates(self, mock_get_hazard):
        """緯度経度文字列からハザード情報取得のテスト"""
        # モックの設定
        mock_hazard_data = {
            'jshis_prob_60': {'max_prob': 0.15, 'center_prob': 0.12}
        }
        mock_get_hazard.return_value = mock_hazard_data
        
        result = get_hazard_from_input("35.6586, 139.7454")
        
        assert result['status'] == 'success'
        assert result['input_type'] == 'latlon'
        assert result['source'] == '座標: 35.6586, 139.7454'
        assert result['coordinates']['latitude'] == 35.6586
        assert result['coordinates']['longitude'] == 139.7454
        assert result['hazard_info'] == mock_hazard_data
        
        mock_get_hazard.assert_called_once_with(35.6586, 139.7454)
    
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    @patch('hazard_api_function.geocoding.geocode')
    @patch('hazard_api_function.suumo_scraper.extract_address_from_suumo')
    def test_get_hazard_from_input_suumo_url(self, mock_scraper, mock_geocode, mock_get_hazard):
        """SUUMO URLからハザード情報取得のテスト"""
        # モックの設定
        mock_scraper.return_value = "東京都新宿区西新宿1-1-1"
        mock_geocode.return_value = (35.6586, 139.7454)
        mock_hazard_data = {
            'tsunami_inundation': {'max_info': '浸水想定なし', 'center_info': '浸水想定なし'}
        }
        mock_get_hazard.return_value = mock_hazard_data
        
        result = get_hazard_from_input("https://suumo.jp/chintai/tokyo/example")
        
        assert result['status'] == 'success'
        assert result['input_type'] == 'suumo_url'
        assert result['source'] == 'SUUMO物件: 東京都新宿区西新宿1-1-1'
        assert result['coordinates']['latitude'] == 35.6586
        assert result['coordinates']['longitude'] == 139.7454
        assert result['hazard_info']['property_address'] == "東京都新宿区西新宿1-1-1"
        
        mock_scraper.assert_called_once_with("https://suumo.jp/chintai/tokyo/example")
        mock_geocode.assert_called_once_with("東京都新宿区西新宿1-1-1")
        mock_get_hazard.assert_called_once_with(35.6586, 139.7454)
    
    def test_get_hazard_from_input_invalid_url(self):
        """無効なURLのテスト"""
        result = get_hazard_from_input("https://example.com/invalid")
        
        assert 'error' in result
        assert result['error'] == 'Invalid URL'
        assert '無効なURL' in result['message']
    
    def test_get_hazard_from_input_invalid_coordinates(self):
        """無効な緯度経度のテスト"""
        result = get_hazard_from_input("abc, def")
        
        assert 'error' in result
        assert result['error'] == 'Geocoding error'
        assert '住所の変換中にエラー' in result['message']
    
    def test_get_hazard_from_input_invalid_coordinate_format(self):
        """緯度経度形式で座標範囲外の値のテスト"""
        result = get_hazard_from_input("50.0, 140.0")
        
        assert 'error' in result
        assert result['error'] == 'Invalid coordinates'
        assert '緯度は24.0〜46.0の範囲' in result['message']
    
    @patch('hazard_api_function.geocoding.geocode')
    def test_get_hazard_from_input_geocoding_failure(self, mock_geocode):
        """ジオコーディング失敗のテスト"""
        mock_geocode.return_value = (None, None)
        
        result = get_hazard_from_input("存在しない住所")
        
        assert 'error' in result
        assert result['error'] == 'Location not found'
        assert '場所を特定できませんでした' in result['message']
    
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    def test_input_parameter_get_request(self, mock_get_hazard):
        """GETリクエストでinputパラメータを使用するテスト"""
        mock_hazard_data = {'test': 'data'}
        mock_get_hazard.return_value = mock_hazard_data
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {
                'input': '35.6586, 139.7454'
            }
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'success'
        assert body['input_type'] == 'latlon'
        assert body['source'] == '座標: 35.6586, 139.7454'
    
    @patch('hazard_api_function.geocoding.geocode')
    @patch('hazard_api_function.hazard_info.get_all_hazard_info')
    def test_input_parameter_post_request_address(self, mock_get_hazard, mock_geocode):
        """POSTリクエストで住所入力のテスト"""
        mock_geocode.return_value = (35.6586, 139.7454)
        mock_hazard_data = {'test': 'data'}
        mock_get_hazard.return_value = mock_hazard_data
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'input': '東京都新宿区'
            })
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'success'
        assert body['input_type'] == 'address'
        assert body['source'] == '住所: 東京都新宿区'
        
        mock_geocode.assert_called_once_with('東京都新宿区')
    
    def test_backwards_compatibility(self):
        """既存のlat/lonパラメータでの後方互換性テスト"""
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {}
        }
        
        result = lambda_handler(event, None)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['error'] == 'Missing parameters'
        assert 'Either input parameter or both lat and lon parameters are required' in body['message']
        assert 'examples' in body