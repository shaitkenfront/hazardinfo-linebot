import json
from app import input_parser, geocoding, line_handler, hazard_api_client, display_formatter

def get_formatted_hazard_data(text: str) -> tuple[str, dict | None]:
    """
    ユーザー入力に基づいてハザード情報を取得し、整形されたデータを返す。
    エラーメッセージと整形済みハザード情報のタプルを返す。
    """
    input_type, value = input_parser.parse_input_type(text)
    lat, lon = None, None
    address_info = ""

    if input_type == 'latlon':
        try:
            lat, lon = map(float, value.split(','))
            address_info = f"座標「{value}」のハザード情報です。"
        except ValueError:
            return "緯度・経度の形式が正しくありません。例: 35.6586, 139.7454", None, ""

    elif input_type == 'invalid_url':
        return "無効なURLです。住所または緯度経度を入力してください。", None, ""
    
    elif input_type == 'address':
        lat, lon = geocoding.geocode(value)
        address_info = f"「{value}」周辺のハザード情報です。"

    if lat is None or lon is None:
        return "場所を特定できませんでした。住所やURLを確認してください。", None, ""

    # ハザード情報を取得 (REST API経由)
    try:
        api_client = hazard_api_client.HazardAPIClient()
        api_response = api_client.get_hazard_info(lat, lon)
        raw_hazards = hazard_api_client.convert_api_response_to_legacy_format(api_response)
    except Exception as e:
        print(f"Error fetching hazard info from REST API: {e}")
        return f"ハザード情報の取得に失敗しました。エラー: {str(e)}", None, ""


    # 応答メッセージを整形
    formatted_hazards = display_formatter.format_all_hazard_info_for_display(raw_hazards)
    
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
    line_result = line_handler.handle_line_event(body, signature, get_hazard_response)
    
    # テストモードの場合はLINE処理結果を応答に含める
    if line_result and line_result.get('test_mode'):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'OK',
                'test_mode': True,
                'line_processing_result': line_result
            }, ensure_ascii=False)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
