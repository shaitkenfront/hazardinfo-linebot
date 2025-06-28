import requests
import json
import math

# J-SHIS API 地点別確率値APIのベースURL (2020年版、平均、全期間)
JSHIS_API_URL_BASE = "https://www.j-shis.bosai.go.jp/map/api/pshm/Y2020/AVR/TTL_MTTL/meshinfo.geojson"

# 国土地理院WMS GetFeatureInfo エンドポイント
WMS_GETFEATUREINFO_BASE_URL = "https://disaportal.gsi.go.jp/maps/wms/hazardmap?"

# WMSレイヤー設定
WMS_LAYERS = {
    '想定最大浸水深': 'fldareak_l2',
    '土砂災害警戒区域': 'dosha_keikai',
    '土砂災害特別警戒区域': 'dosha_tokubetsu_keikai',
    '大規模盛土造成地': 'morido_daikibo',
}

def _format_jshis_probability(prob_value) -> str:
    """
    J-SHISから取得した確率値をフォーマットする。
    Noneの場合や解析エラーの場合は「データなし」を返す。
    """
    if prob_value is not None:
        try:
            prob_float = float(prob_value)
            return f"{math.floor(prob_float * 100)}%"
        except ValueError:
            return 'データ解析失敗'
    return 'データなし'

def get_jshis_info(lat: float, lon: float) -> dict[str, str]:
    """
    指定された緯度経度における地震発生確率を取得する。
    J-SHIS 地点別確率値APIを使用。
    """
    results = {}

    # 震度5強以上の確率を取得
    params_50 = {
        'position': f'{lon},{lat}',
        'epsg': 4326,
        'type': 'T30_I50_PS' # このAPIではtypeパラメータは不要かもしれないが、念のため残す
    }
    try:
        response_50 = requests.get(JSHIS_API_URL_BASE, params=params_50, timeout=10)
        response_50.raise_for_status()
        geojson_50 = response_50.json()
        
        prob_50 = None
        if geojson_50.get('features') and geojson_50['features'][0].get('properties'):
            prob_50 = geojson_50['features'][0]['properties'].get('T30_I50_PS')
        results['今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）'] = _format_jshis_probability(prob_50)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching J-SHIS 50 data: {e}")
        results['今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）'] = '取得失敗'
    except json.JSONDecodeError:
        print("Error decoding J-SHIS 50 GeoJSON.")
        results['今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）'] = 'データ解析失敗'

    # 震度6強以上の確率を取得
    params_60 = {
        'position': f'{lon},{lat}',
        'epsg': 4326,
        'type': 'T30_I60_PS' # このAPIではtypeパラメータは不要かもしれないが、念のため残す
    }
    try:
        response_60 = requests.get(JSHIS_API_URL_BASE, params=params_60, timeout=10)
        response_60.raise_for_status()
        geojson_60 = response_60.json()

        prob_60 = None
        if geojson_60.get('features') and geojson_60['features'][0].get('properties'):
            prob_60 = geojson_60['features'][0]['properties'].get('T30_I60_PS')
        results['今後30年以内に震度6強以上の地震が起こる確率（J-SHIS）'] = _format_jshis_probability(prob_60)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching J-SHIS 60 data: {e}")
        results['今後30年以内に震度6強以上の地震が起こる確率（J-SHIS）'] = '取得失敗'
    except json.JSONDecodeError:
        print("Error decoding J-SHIS 60 GeoJSON.")
        results['今後30年以内に震度6強以上の地震が起こる確率（J-SHIS）'] = 'データ解析失敗'

    return results

def get_wms_info(lat: float, lon: float) -> dict[str, str]:
    """
    国土地理院WMSから指定された緯度経度のハザード情報を取得する。
    (現状はダミーデータ)
    """
    results = {}
    
    # 簡易的なBBOXとピクセル座標の計算
    # 緯度経度を中央に、小さな範囲でBBOXを設定
    delta = 0.0001 # 緯度経度で約10m程度の範囲
    bbox = f"{lon - delta},{lat - delta},{lon + delta},{lat + delta}"
    width, height = 101, 101 # 適当な画像サイズ
    x, y = 50, 50 # 画像の中心ピクセル

    for hazard_name, layer_name in WMS_LAYERS.items():
        params = {
            'SERVICE': 'WMS',
            'VERSION': '1.1.1',
            'REQUEST': 'GetFeatureInfo',
            'QUERY_LAYERS': layer_name,
            'LAYERS': layer_name,
            'BBOX': bbox,
            'FEATURE_COUNT': 1,
            'HEIGHT': height,
            'WIDTH': width,
            'FORMAT': 'image/png', # 画像フォーマットはダミー、実際には使われない
            'INFO_FORMAT': 'application/json', # JSON形式での情報取得を試みる
            'SRS': 'EPSG:4326', # WGS84座標系
            'X': x,
            'Y': y,
        }
        
        try:
            response = requests.get(WMS_GETFEATUREINFO_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            # WMSのGetFeatureInfoの応答はJSONとは限らないため、エラーハンドリングを強化
            try:
                data = response.json()
                # ここでJSONデータを解析し、必要な情報を抽出
                # 国土地理院WMSのGetFeatureInfoのJSON応答形式に依存
                # 例: data['features'][0]['properties']['value'] など
                if data and data.get('features'):
                    # 浸水深のレイヤーの場合
                    if layer_name == 'fldareak_l2':
                        # 浸水深の具体的なプロパティ名を確認する必要がある
                        # 例: '浸水深' や 'value' など
                        # ここでは仮に 'value' というプロパティがあると想定
                        value = data['features'][0]['properties'].get('value', '情報なし')
                        results[hazard_name] = f"{value}m" if value != '情報なし' else '情報なし'
                    else:
                        # その他のレイヤー（土砂災害、盛土など）は該当有無を判定
                        results[hazard_name] = '該当あり'
                else:
                    results[hazard_name] = '該当なし'

            except json.JSONDecodeError:
                # JSONでない場合はテキストとして処理（HTMLやXMLの場合）
                # ここでは簡易的に「該当あり」か「該当なし」を判定
                if "該当" in response.text or "あり" in response.text: # 非常に簡易的な判定
                    results[hazard_name] = '該当あり'
                else:
                    results[hazard_name] = '該当なし'
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching WMS data for {layer_name}: {e}")
            results[hazard_name] = '取得失敗'
            
    return results

def get_all_hazard_info(lat: float, lon: float) -> dict[str, str]:
    """
    すべてのハザード情報をまとめて取得する。
    """
    hazard_info = {}
    hazard_info.update(get_jshis_info(lat, lon))
    hazard_info.update(get_wms_info(lat, lon))
    return hazard_info
