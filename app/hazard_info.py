import requests
import json

# J-SHIS API エンドポイント
JSHIS_API_URL_50 = "https://www.j-shis.bosai.go.jp/map/api/s/jma/api/JMA_OPR_MEC_T30_I50_PS_A.geojson"
JSHIS_API_URL_60 = "https://www.j-shis.bosai.go.jp/map/api/s/jma/api/JMA_OPR_MEC_T30_I60_PS_A.geojson"

# 国土地理院WMS GetFeatureInfo エンドポイント
WMS_GETFEATUREINFO_URL = "https://disaportal.gsi.go.jp/maps/wms/hazardmap?"

# WMSレイヤー設定 (現状はダミー)
WMS_LAYERS = {
    'flood': 'fldareak_l2',
    'sediment_alert': 'dosha_keikai',
    'sediment_special_alert': 'dosha_tokubetsu_keikai',
    'large_scale_embankment': 'morido_daikibo',
}

def latlon_to_mesh_code(lat: float, lon: float) -> str:
    """
    緯度経度から3次地域メッシュコードを計算する。
    参考: https://www.gsi.go.jp/kihonjohochousa/kihonjohochousa40006.html
    """
    # 1次メッシュ
    p = lat * 1.5
    u = int(p)
    v = int(lon - 100)

    # 2次メッシュ
    p_rem = p - u
    v_rem = lon - 100 - v
    w = int(p_rem * 8)
    x = int(v_rem * 8)

    # 3次メッシュ
    w_rem = (p_rem * 8) - w
    x_rem = (v_rem * 8) - x
    y = int(w_rem * 10)
    z = int(x_rem * 10)

    return f"{u:02d}{v:02d}{w}{x}{y}{z}"

def get_jshis_info(lat: float, lon: float) -> dict[str, str]:
    """
    指定された緯度経度における地震発生確率を取得する。
    """
    mesh_code = latlon_to_mesh_code(lat, lon)
    results = {}

    # 震度5強以上の確率を取得
    try:
        response_50 = requests.get(JSHIS_API_URL_50, timeout=10)
        response_50.raise_for_status()
        geojson_50 = response_50.json()
        
        found_50 = False
        for feature in geojson_50.get('features', []):
            if feature.get('properties', {}).get('meshcode') == mesh_code:
                results['今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）'] = f"{feature['properties']['T30_I50_PS']}%"
                found_50 = True
                break
        if not found_50:
            results['今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）'] = 'データなし'

    except requests.exceptions.RequestException as e:
        print(f"Error fetching J-SHIS 50 data: {e}")
        results['今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）'] = '取得失敗'
    except json.JSONDecodeError:
        print("Error decoding J-SHIS 50 GeoJSON.")
        results['今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）'] = 'データ解析失敗'

    # 震度6強以上の確率を取得
    try:
        response_60 = requests.get(JSHIS_API_URL_60, timeout=10)
        response_60.raise_for_status()
        geojson_60 = response_60.json()

        found_60 = False
        for feature in geojson_60.get('features', []):
            if feature.get('properties', {}).get('meshcode') == mesh_code:
                results['今後30年以内に震度6強以上の地震が起こる確率（J-SHIS）'] = f"{feature['properties']['T30_I60_PS']}%"
                found_60 = True
                break
        if not found_60:
            results['今後30年以内に震度6強以上の地震が起こる確率（J-SHIS）'] = 'データなし'

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
    # WMSのGetFeatureInfoはピクセル単位での問い合わせが必要
    # ここではAPI仕様の概要を示すもので、完全な実装ではない
    # 実際には地図のBBOXと画像のXY座標を計算してリクエストする
    
    # ダミーデータで応答
    results["想定最大浸水深"] = "0.5m ~ 3.0m未満"
    results["土砂災害警戒区域・特別警戒区域の該当有無"] = "範囲外"
    results["大規模盛土造成地の該当有無"] = "該当なし"
    
    return results

def get_all_hazard_info(lat: float, lon: float) -> dict[str, str]:
    """
    すべてのハザード情報をまとめて取得する。
    """
    hazard_info = {}
    hazard_info.update(get_jshis_info(lat, lon))
    hazard_info.update(get_wms_info(lat, lon))
    return hazard_info