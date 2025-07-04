import json
from src.app import input_parser, geocoding, suumo_scraper, hazard_info, line_handler

def get_formatted_hazard_data(text: str) -> tuple[str, dict | None]:
    """
    ユーザー入力に基づいてハザード情報を取得し、整形されたデータを返す。
    エラーメッセージと整形済みハザード情報のタプルを返す。
    """
    input_type, value = input_parser.parse_input_type(text)
    lat, lon = None, None
    property_address = None

    if input_type == 'latlon':
        try:
            lat, lon = map(float, value.split(','))
        except ValueError:
            return "緯度・経度の形式が正しくありません。例: 35.6586, 139.7454", None, ""

    elif input_type == 'suumo_url':
        property_address = suumo_scraper.extract_address_from_suumo(value)
        if not property_address:
            return "SUUMOのURLから住所を取得できませんでした。", None, ""
        lat, lon = geocoding.geocode(property_address)
        address_info = f"SUUMO物件のハザード情報です。"

    elif input_type == 'invalid_url':
        return "無効なURLです。SUUMOの物件詳細ページのURLを入力してください。", None, ""
    
    elif input_type == 'address':
        lat, lon = geocoding.geocode(value)
        address_info = f"「{value}」周辺のハザード情報です。"

    if lat is None or lon is None:
        return "場所を特定できませんでした。住所やURLを確認してください。", None, ""

    # ハザード情報を取得
    raw_hazards = hazard_info.get_all_hazard_info(lat, lon)

    # SUUMO URLの場合、スクレイピングした住所をハザード情報に追加
    if input_type == 'suumo_url':
        raw_hazards['property_address'] = property_address

    # 応答メッセージを整形
    formatted_hazards = hazard_info.format_all_hazard_info_for_display(raw_hazards)
    
    return None, formatted_hazards, address_info

def get_hazard_response(text: str) -> str:
    error_message, formatted_hazards, initial_greeting_message = get_formatted_hazard_data(text)

    if error_message:
        return error_message

    # 応答メッセージを整形
    response_lines = [initial_greeting_message, "-" * 20]
    for key, val in formatted_hazards.items():
        response_lines.append(f"【{key}】\n{val}")
    
    return "\n".join(response_lines)

def lambda_handler(event, context):
    """
    AWS Lambdaのメインハンドラ関数。
    """
    # LINEからのWebhookか確認
    signature = event['headers'].get('x-line-signature')
    body = event['body']

    if not signature:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing X-Line-Signature')
        }

    # LINEイベント処理
    line_handler.handle_line_event(body, signature, get_hazard_response)
    
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
