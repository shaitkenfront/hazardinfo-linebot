import json
import boto3
from app import hazard_info, input_parser, geocoding, suumo_scraper


def validate_coordinates(lat, lon):
    """
    緯度経度の妥当性を検証する
    """
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        
        # 日本の緯度経度の範囲をチェック
        if not (24.0 <= lat_float <= 46.0):
            return False, "緯度は24.0〜46.0の範囲で入力してください"
        
        if not (123.0 <= lon_float <= 146.0):
            return False, "経度は123.0〜146.0の範囲で入力してください"
            
        return True, None
    except ValueError:
        return False, "緯度・経度は数値で入力してください"


def get_hazard_from_input(input_text):
    """
    住所、URL、緯度経度のいずれかの入力からハザード情報を取得する
    """
    input_type, value = input_parser.parse_input_type(input_text)
    lat, lon = None, None
    property_address = None
    source_info = ""
    
    if input_type == 'latlon':
        try:
            lat, lon = map(float, value.split(','))
            source_info = f"座標: {lat}, {lon}"
        except ValueError:
            return {
                'error': 'Invalid coordinate format',
                'message': '緯度・経度の形式が正しくありません。例: 35.6586, 139.7454'
            }
    
    elif input_type == 'suumo_url':
        try:
            property_address = suumo_scraper.extract_address_from_suumo(value)
            if not property_address:
                return {
                    'error': 'SUUMO address extraction failed',
                    'message': 'SUUMOのURLから住所を取得できませんでした。'
                }
            lat, lon = geocoding.geocode(property_address)
            source_info = f"SUUMO物件: {property_address}"
        except Exception as e:
            return {
                'error': 'SUUMO processing error',
                'message': f'SUUMO URLの処理中にエラーが発生しました: {str(e)}'
            }
    
    elif input_type == 'invalid_url':
        return {
            'error': 'Invalid URL',
            'message': '無効なURLです。SUUMOの物件詳細ページのURLを入力してください。'
        }
    
    elif input_type == 'address':
        try:
            lat, lon = geocoding.geocode(value)
            source_info = f"住所: {value}"
        except Exception as e:
            return {
                'error': 'Geocoding error',
                'message': f'住所の変換中にエラーが発生しました: {str(e)}'
            }
    
    if lat is None or lon is None:
        return {
            'error': 'Location not found',
            'message': '場所を特定できませんでした。住所やURLを確認してください。'
        }
    
    # 日本の範囲チェック
    is_valid, error_message = validate_coordinates(lat, lon)
    if not is_valid:
        return {
            'error': 'Invalid coordinates',
            'message': error_message
        }
    
    # ハザード情報を取得
    hazard_data = hazard_info.get_all_hazard_info(lat, lon)
    
    # SUUMO URLの場合、スクレイピングした住所をハザード情報に追加
    if input_type == 'suumo_url' and property_address:
        hazard_data['property_address'] = property_address
    
    return {
        'coordinates': {
            'latitude': lat,
            'longitude': lon
        },
        'source': source_info,
        'input_type': input_type,
        'hazard_info': hazard_data,
        'status': 'success'
    }


def lambda_handler(event, context):
    """
    REST APIで緯度経度を受け取ってハザード情報を返すLambda関数
    """
    try:
        # CORSヘッダーの設定
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }
        
        # OPTIONSリクエスト（プリフライトリクエスト）への対応
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight response'})
            }
        
        # HTTPメソッドのチェック
        if event.get('httpMethod') not in ['GET', 'POST']:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Method not allowed',
                    'message': 'Only GET and POST methods are supported'
                })
            }
        
        # パラメータの取得
        lat = None
        lon = None
        input_text = None
        
        if event.get('httpMethod') == 'GET':
            # GETリクエストの場合、クエリパラメータから取得
            query_params = event.get('queryStringParameters') or {}
            lat = query_params.get('lat')
            lon = query_params.get('lon')
            input_text = query_params.get('input')  # 住所やURLを受け取る新しいパラメータ
        
        elif event.get('httpMethod') == 'POST':
            # POSTリクエストの場合、リクエストボディから取得
            body = event.get('body', '{}')
            if body:
                try:
                    body_data = json.loads(body)
                    lat = body_data.get('lat')
                    lon = body_data.get('lon')
                    input_text = body_data.get('input')  # 住所やURLを受け取る新しいパラメータ
                except json.JSONDecodeError:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'error': 'Invalid JSON',
                            'message': 'Request body must be valid JSON'
                        })
                    }
        
        # 入力方法を判定
        if input_text:
            # 住所・URL・座標文字列による入力
            print(f"Processing input text: {input_text}")
            result = get_hazard_from_input(input_text)
            
            # エラーの場合
            if 'error' in result:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps(result)
                }
            
            # 成功の場合
            response_data = result
            
        elif lat is not None and lon is not None:
            # 従来の緯度経度による直接入力
            # 緯度経度の妥当性検証
            is_valid, error_message = validate_coordinates(lat, lon)
            if not is_valid:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Invalid coordinates',
                        'message': error_message
                    })
                }
            
            # ハザード情報を取得
            lat_float = float(lat)
            lon_float = float(lon)
            
            print(f"Fetching hazard info for coordinates: {lat_float}, {lon_float}")
            
            # ハザード情報の取得
            hazard_data = hazard_info.get_all_hazard_info(lat_float, lon_float)
            
            # レスポンスの構築
            response_data = {
                'coordinates': {
                    'latitude': lat_float,
                    'longitude': lon_float
                },
                'source': f"座標: {lat_float}, {lon_float}",
                'input_type': 'latlon',
                'hazard_info': hazard_data,
                'status': 'success'
            }
        
        else:
            # パラメータが不足している場合
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing parameters',
                    'message': 'Either input parameter or both lat and lon parameters are required',
                    'examples': {
                        'coordinate_input': {
                            'GET': '?lat=35.6586&lon=139.7454',
                            'POST': '{"lat": 35.6586, "lon": 139.7454}'
                        },
                        'flexible_input': {
                            'GET': '?input=東京都新宿区',
                            'POST': '{"input": "東京都新宿区"}'
                        },
                        'suumo_input': {
                            'GET': '?input=https://suumo.jp/chintai/tokyo/example',
                            'POST': '{"input": "https://suumo.jp/chintai/tokyo/example"}'
                        }
                    }
                })
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': f'An error occurred while processing the request: {str(e)}'
            })
        }