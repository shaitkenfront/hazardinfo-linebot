import json
from app import input_parser, geocoding, suumo_scraper, hazard_info, line_handler

def get_hazard_response(text: str) -> str:
    """
    ユーザー入力に基づいてハザード情報を生成し、応答メッセージを作成する。
    """
    input_type, value = input_parser.parse_input_type(text)
    lat, lon = None, None
    address_info = ""

    if input_type == 'latlon':
        try:
            lat, lon = map(float, value.split(','))
            address_info = f"指定された座標（{lat}, {lon}）周辺のハザード情報です。"
        except ValueError:
            return "緯度・経度の形式が正しくありません。例: 35.6586, 139.7454"

    elif input_type == 'suumo_url':
        address = suumo_scraper.extract_address_from_suumo(value)
        if not address:
            return "SUUMOのURLから住所を取得できませんでした。"
        lat, lon = geocoding.geocode(address)
        address_info = f"「{value} （{address}）」周辺のハザード情報です。"

    elif input_type == 'invalid_url':
        return "無効なURLです。SUUMOの物件詳細ページのURLを入力してください。"
    
    elif input_type == 'address':
        lat, lon = geocoding.geocode(value)
        address_info = f"「{value}」周辺のハザード情報です。"

    if lat is None or lon is None:
        return "場所を特定できませんでした。住所やURLを確認してください。"

    # ハザード情報を取得
    hazards = hazard_info.get_all_hazard_info(lat, lon)

    # SUUMO URLの場合、スクレイピングした住所をハザード情報に追加
    if input_type == 'suumo_url':
        # address変数はsuumo_urlのブロック内で定義済み
        hazards['物件住所'] = address

    # 応答メッセージを整形
    response_lines = [address_info, "-" * 20]
    for key, val in hazards.items():
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
