import json
import boto3
from app import hazard_info


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
        
        if event.get('httpMethod') == 'GET':
            # GETリクエストの場合、クエリパラメータから取得
            query_params = event.get('queryStringParameters') or {}
            lat = query_params.get('lat')
            lon = query_params.get('lon')
        
        elif event.get('httpMethod') == 'POST':
            # POSTリクエストの場合、リクエストボディから取得
            body = event.get('body', '{}')
            if body:
                try:
                    body_data = json.loads(body)
                    lat = body_data.get('lat')
                    lon = body_data.get('lon')
                except json.JSONDecodeError:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'error': 'Invalid JSON',
                            'message': 'Request body must be valid JSON'
                        })
                    }
        
        # 必須パラメータの確認
        if lat is None or lon is None:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Missing parameters',
                    'message': 'Both lat and lon parameters are required',
                    'example': {
                        'GET': '?lat=35.6586&lon=139.7454',
                        'POST': '{"lat": 35.6586, "lon": 139.7454}'
                    }
                })
            }
        
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
            'hazard_info': hazard_data,
            'status': 'success'
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