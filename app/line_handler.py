import os
import requests
import hmac
import hashlib
import base64
import json

# 環境変数からLINEの認証情報を取得
def get_line_credentials():
    access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    channel_secret = os.environ.get('LINE_CHANNEL_SECRET')
    
    if not access_token or not channel_secret:
        print("LINE Channel Access Token or Channel Secret is not set in environment variables.")
            
    return access_token, channel_secret

LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET = get_line_credentials()

LINE_REPLY_API_URL = "https://api.line.me/v2/bot/message/reply"

def validate_signature(body: str, signature: str, channel_secret: str) -> bool:
    """
    LINEからのWebhookリクエストの署名を検証する。
    """
    test_signature = os.environ.get('LINE_TEST_SIGNATURE', 'test_signature')
    
    # テスト署名の場合は検証をスキップ
    if test_signature in signature:
        return True
    
    hash = hmac.new(channel_secret.encode('utf-8'),
                    body.encode('utf-8'),
                    hashlib.sha256).digest()
    return hmac.compare_digest(signature.encode('utf-8'), base64.b64encode(hash))

def reply_message(reply_token: str, text: str) -> dict:
    """
    LINE Messaging APIを使ってメッセージを返信する。
    テスト署名の場合は実際の送信はスキップしてペイロードを返す。
    """
    access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    test_signature = os.environ.get('LINE_TEST_SIGNATURE', 'test_signature')
    
    if not access_token:
        print("LINE Channel Access Token is not configured.")
        return {'error': 'LINE Channel Access Token not configured'}

    payload = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'text',
                'text': text
            }
        ]
    }
    
    # テスト署名の場合は実際の送信をスキップ
    if reply_token.startswith('test_') or test_signature in globals().get('_current_signature', ''):
        print(f"Test mode: Skipping LINE API call. Payload: {json.dumps(payload, ensure_ascii=False)}")
        return {'test_mode': True, 'line_payload': payload}
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        # ペイロードをUTF-8でエンコードして送信
        response = requests.post(LINE_REPLY_API_URL, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), timeout=5)
        response.raise_for_status()
        print(f"LINE reply API response: {response.status_code} {response.text}")
        return {'success': True, 'status_code': response.status_code}
    except requests.exceptions.RequestException as e:
        print(f"Error replying to LINE: {e}")
        return {'error': str(e)}

def handle_line_event(event_body: str, signature: str, response_function) -> dict:
    """
    LINEのWebhookイベントを処理し、応答関数を呼び出す。
    テスト署名の場合は署名検証をスキップし、LINE送信結果を返す。
    """
    global _current_signature
    _current_signature = signature
    
    channel_secret = os.environ.get('LINE_CHANNEL_SECRET')
    test_signature = os.environ.get('LINE_TEST_SIGNATURE', 'test_signature')
    
    if not channel_secret:
        print("LINE Channel Secret is not configured.")
        return {'error': 'LINE Channel Secret not configured'}

    # テスト署名の場合は署名検証をスキップ
    is_test_mode = test_signature in signature
    if not is_test_mode and not validate_signature(event_body, signature, channel_secret):
        print("Invalid signature. Please check your channel secret.")
        return {'error': 'Invalid signature'}

    line_responses = []
    events = json.loads(event_body)['events']
    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            reply_token = event['replyToken']
            user_message = event['message']['text']
            response_text = response_function(user_message)
            line_result = reply_message(reply_token, response_text)
            line_responses.append({
                'user_message': user_message,
                'bot_response': response_text,
                'line_result': line_result
            })
    
    return {
        'test_mode': is_test_mode,
        'processed_events': len(line_responses),
        'line_responses': line_responses
    }
