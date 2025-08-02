import pytest
import json
import responses
from unittest.mock import patch, MagicMock
from app.line_handler import validate_signature, reply_message, handle_line_event


class TestLineHandler:
    
    def test_validate_signature_valid(self):
        body = "test_body"
        secret = "test_secret"
        
        # 正しい署名を計算
        import hmac
        import hashlib
        import base64
        
        hash_value = hmac.new(secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
        expected_signature = base64.b64encode(hash_value).decode('utf-8')
        
        result = validate_signature(body, expected_signature, secret)
        assert result is True
    
    def test_validate_signature_invalid(self):
        body = "test_body"
        signature = "invalid_signature"
        secret = "test_secret"
        
        result = validate_signature(body, signature, secret)
        assert result is False
    
    @responses.activate
    def test_reply_message_success(self):
        responses.add(
            responses.POST,
            "https://api.line.me/v2/bot/message/reply",
            json={},
            status=200
        )
        
        with patch.dict('os.environ', {'LINE_CHANNEL_ACCESS_TOKEN': 'test_token'}):
            reply_message("test_token", "test_message")
    
    def test_reply_message_no_token(self):
        with patch.dict('os.environ', {}, clear=True):
            with patch('builtins.print') as mock_print:
                reply_message("test_token", "test_message")
                mock_print.assert_called_with("LINE Channel Access Token is not configured.")
    
    @patch('app.line_handler.validate_signature')
    @patch('app.line_handler.reply_message')
    def test_handle_line_event_success(self, mock_reply, mock_validate):
        mock_validate.return_value = True
        
        event_body = json.dumps({
            "events": [
                {
                    "type": "message",
                    "message": {
                        "type": "text",
                        "text": "test_message"
                    },
                    "replyToken": "test_reply_token"
                }
            ]
        })
        
        response_function = MagicMock(return_value="test_response")
        
        with patch.dict('os.environ', {'LINE_CHANNEL_SECRET': 'test_secret'}):
            handle_line_event(event_body, "test_signature", response_function)
        
        mock_reply.assert_called_once_with("test_reply_token", "test_response")
        response_function.assert_called_once_with("test_message")
    
    @patch('app.line_handler.validate_signature')
    def test_handle_line_event_invalid_signature(self, mock_validate):
        mock_validate.return_value = False
        
        with patch.dict('os.environ', {'LINE_CHANNEL_SECRET': 'test_secret'}):
            with patch('builtins.print') as mock_print:
                handle_line_event("test_body", "invalid_signature", lambda x: x)
                mock_print.assert_called_with("Invalid signature. Please check your channel secret.")
    
    def test_handle_line_event_no_secret(self):
        with patch.dict('os.environ', {}, clear=True):
            with patch('builtins.print') as mock_print:
                handle_line_event("test_body", "test_signature", lambda x: x)
                mock_print.assert_called_with("LINE Channel Secret is not configured.")
    
    @patch('app.line_handler.validate_signature')
    def test_handle_line_event_non_text_message(self, mock_validate):
        mock_validate.return_value = True
        
        event_body = json.dumps({
            "events": [
                {
                    "type": "message",
                    "message": {
                        "type": "image"
                    },
                    "replyToken": "test_reply_token"
                }
            ]
        })
        
        response_function = MagicMock()
        
        with patch.dict('os.environ', {'LINE_CHANNEL_SECRET': 'test_secret'}):
            handle_line_event(event_body, "test_signature", response_function)
        
        response_function.assert_not_called()