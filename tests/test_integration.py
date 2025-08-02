import pytest
import json
import responses
from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler


class TestIntegration:
    
    @responses.activate
    @patch('lambda_function.hazard_info.get_all_hazard_info')
    @patch('lambda_function.hazard_info.format_all_hazard_info_for_display')
    def test_full_workflow_address_input(self, mock_format, mock_get_hazard):
        # モックの設定
        mock_get_hazard.return_value = {'flood': 'low', 'landslide': 'medium'}
        mock_format.return_value = {'洪水': '低リスク', '土砂災害': '中リスク'}
        
        # Geocoding APIのモック
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
        
        # LINE Reply APIのモック
        responses.add(
            responses.POST,
            "https://api.line.me/v2/bot/message/reply",
            json={},
            status=200
        )
        
        # LINEイベントの構成
        line_event = {
            "events": [
                {
                    "type": "message",
                    "message": {
                        "type": "text",
                        "text": "東京都新宿区"
                    },
                    "replyToken": "test_reply_token"
                }
            ]
        }
        
        event_body = json.dumps(line_event)
        
        # 正しい署名を計算
        import hmac
        import hashlib
        import base64
        
        secret = "test_secret"
        hash_value = hmac.new(secret.encode('utf-8'), event_body.encode('utf-8'), hashlib.sha256).digest()
        expected_signature = base64.b64encode(hash_value).decode('utf-8')
        
        lambda_event = {
            'headers': {'x-line-signature': expected_signature},
            'body': event_body
        }
        
        # 環境変数の設定
        with patch.dict('os.environ', {
            'LINE_CHANNEL_ACCESS_TOKEN': 'test_token',
            'LINE_CHANNEL_SECRET': 'test_secret',
            'GOOGLE_API_KEY': 'test_key'
        }):
            result = lambda_handler(lambda_event, None)
        
        assert result['statusCode'] == 200
        assert result['body'] == '"OK"'
        
        # API呼び出しの確認
        assert len(responses.calls) == 2  # Geocoding API + LINE Reply API
    
    
    def test_invalid_signature_integration(self):
        lambda_event = {
            'headers': {'x-line-signature': 'invalid_signature'},
            'body': '{"events": []}'
        }
        
        with patch.dict('os.environ', {
            'LINE_CHANNEL_SECRET': 'test_secret'
        }):
            result = lambda_handler(lambda_event, None)
        
        assert result['statusCode'] == 200  # LINE handler内で署名検証エラーが処理される
    
    def test_missing_environment_variables(self):
        lambda_event = {
            'headers': {'x-line-signature': 'test_signature'},
            'body': '{"events": []}'
        }
        
        with patch.dict('os.environ', {}, clear=True):
            result = lambda_handler(lambda_event, None)
        
        assert result['statusCode'] == 200