import requests
import json
import math
from PIL import Image
from io import BytesIO
from shapely.geometry import shape, Point
from app import geocoding, geojsonhelper

# J-SHIS API 地点別確率値APIのベースURL (2020年版、平均、全期間)
JSHIS_API_URL_BASE = "https://www.j-shis.bosai.go.jp/map/api/pshm/Y2020/AVR/TTL_MTTL/meshinfo.geojson"

# 国土地理院WMS GetFeatureInfo エンドポイント
WMS_GETFEATUREINFO_BASE_URL = "https://disaportal.gsi.go.jp/maps/wms/hazardmap?"

# 想定最大浸水深タイルURL
FLOOD_TILE_URL = "https://disaportaldata.gsi.go.jp/raster/01_flood_l2_shinsuishin_data/{z}/{x}/{y}.png"
FLOOD_TILE_ZOOM = 17 # ズームレベル固定

# 土石流警戒区域・特別警戒区域URL
DEBRIS_FLOW_TILE_URL = "https://disaportaldata.gsi.go.jp/raster/05_dosekiryukeikaikuiki/{z}/{x}/{y}.png"
DEBRIS_FLOW_TILE_ZOOM = 17 # ズームレベル固定

# 急傾斜地の崩壊警戒区域URL
STEEP_SLOPE_TILE_URL = "https://disaportaldata.gsi.go.jp/raster/05_kyukeishakeikaikuiki/{z}/{x}/{y}.png"
STEEP_SLOPE_TILE_ZOOM = 17 # ズームレベル固定

# 地すべり警戒区域タイルURL
LANDSLIDE_TILE_URL = "https://disaportaldata.gsi.go.jp/raster/05_jisuberikeikaikuiki/{z}/{x}/{y}.png"
LANDSLIDE_TILE_ZOOM = 17 # ズームレベル固定

# 津波浸水想定タイルURL
TSUNAMI_TILE_URL = "https://disaportaldata.gsi.go.jp/raster/04_tsunami_newlegend_data/{z}/{x}/{y}.png"
TSUNAMI_TILE_ZOOM = 17 # ズームレベル固定

# 高潮浸水想定タイルURL
HIGH_TIDE_TILE_URL = "https://disaportaldata.gsi.go.jp/raster/03_hightide_l2_shinsuishin_data/{z}/{x}/{y}.png"
HIGH_TIDE_TILE_ZOOM = 17 # ズームレベル固定

# 大規模盛土造成地
S3_LARGE_FILL_LAND_BUCKET = "linebot-hazardinfo-storage-2be2654c-2c7c-001f-a2e7-fadd69e05d62"
S3_LARGE_FILL_LAND_FOLDER = "A54-23_GEOJSON"
S3_LARGE_FILL_LAND_FILE_PREFIX = "A54-23_"


# 浸水深タイルの色と浸水深の対応マップ
INUNDATION_COLOR_MAP = {
    (220,122,220): "20m以上",
    (242,133,201):"10m以上20m未満",
    (255,145,145):"5m以上10m未満",
    (255,183,183):"3m以上5m未満",
    (255,216,192):"0.5m以上3m未満",
    (248,225,166):"0.5m以上1m未満",
    (247,245,169):"0.5m未満",
    (255,255,179):"0.3m未満"
}

# 土石流警戒区域・特別警戒区域タイルの色と浸水深の対応マップ
DEBRIS_FLOW_COLOR_MAP = {
    (165, 0, 33): "土石流特別警戒区域",
    (230, 200, 50): "土石流警戒区域"
}

# 急傾斜地の崩壊警戒区域タイルの色と浸水深の対応マップ
STEEP_SLOPE_COLOR_MAP = {
    (250, 40, 0): "特別警戒区域",
    (250, 230, 0): "警戒区域"
}

# 地すべり警戒区域タイルの色と浸水深の対応マップ
LANDSLIDE_COLOR_MAP = {
    (180, 0, 40): "特別警戒区域",
    (255, 153, 0): "警戒区域"
}

# 津波浸水想定タイルの色と浸水深の対応マップ
TSUNAMI_COLOR_MAP = {
    (220, 122, 220): "20m以上",
    (242, 133, 201): "10m以上20m未満",
    (255, 145, 145): "5m以上10m未満",
    (255, 183, 183): "3m以上5m未満",
    (255, 216, 192): "0.5m以上3m未満",
    (248, 225, 166): "0.5m以上1m未満",
    (247, 245, 169): "0.5m未満",
    (255, 255, 179): "0.3m未満"
}

# 高潮浸水想定タイルの色と浸水深の対応マップ
HIGH_TIDE_COLOR_MAP = {
    (220, 122, 220): "20m以上",
    (242, 133, 201): "10m以上20m未満",
    (255, 145, 145): "5m以上10m未満",
    (255, 183, 183): "3m以上5m未満",
    (255, 216, 192): "0.5m以上3m未満",
    (248, 225, 166): "0.5m以上1m未満",
    (247, 245, 169): "0.5m未満",
    (255, 255, 179): "0.3m未満"
}

# 洪水浸水想定区域タイルの色と浸水深の対応マップ
FLOOD_INUNDATION_COLOR_MAP = {
    (220, 122, 220): "20m以上",
    (242, 133, 201): "10m以上20m未満",
    (255, 145, 145): "5m以上10m未満",
    (255, 183, 183): "3m以上5m未満",
    (255, 216, 192): "0.5m以上3m未満",
    (248, 225, 166): "0.5m以上1m未満",
    (247, 245, 169): "0.5m未満",
    (255, 255, 179): "0.3m未満"
}

def get_tsunami_inundation_info_from_gsi_tile(lat: float, lon: float) -> str:
    """
    国土地理院の津波浸水想定タイル画像から情報を取得する。
    """
    zoom, x_tile, y_tile, px, py = latlon_to_gsi_tile_pixel(lat, lon, TSUNAMI_TILE_ZOOM)
    tile_url = TSUNAMI_TILE_URL.format(z=zoom, x=x_tile, y=y_tile)

    try:
        response = requests.get(tile_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        r, g, b, a = img.getpixel((px, py))
        pixel_rgb = (r, g, b)

        if pixel_rgb in TSUNAMI_COLOR_MAP:
            return TSUNAMI_COLOR_MAP[pixel_rgb]
        elif a == 0:
            return "浸水想定なし"
        else:
            return "情報なし"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching tsunami tile: {e}")
        return "情報なし"
    except Exception as e:
        print(f"Error processing tsunami tile: {e}")
        return "処理失敗"

def get_high_tide_inundation_info_from_gsi_tile(lat: float, lon: float) -> str:
    """
    国土地理院の高潮浸水想定タイル画像から情報を取得する。
    """
    zoom, x_tile, y_tile, px, py = latlon_to_gsi_tile_pixel(lat, lon, HIGH_TIDE_TILE_ZOOM)
    tile_url = HIGH_TIDE_TILE_URL.format(z=zoom, x=x_tile, y=y_tile)

    try:
        response = requests.get(tile_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        r, g, b, a = img.getpixel((px, py))
        pixel_rgb = (r, g, b)

        if pixel_rgb in HIGH_TIDE_COLOR_MAP:
            return HIGH_TIDE_COLOR_MAP[pixel_rgb]
        elif a == 0:
            return "浸水想定なし"
        else:
            return "情報なし"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching storm surge tile: {e}")
        return "情報なし"
    except Exception as e:
        print(f"Error processing storm surge tile: {e}")
        return "処理失敗"

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
        results['今後30年以内に震度5強以上の地震が起こる確率'] = _format_jshis_probability(prob_50)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching J-SHIS 50 data: {e}")
        results['今後30年以内に震度5強以上の地震が起こる確率'] = '取得失敗'
    except json.JSONDecodeError:
        print("Error decoding J-SHIS 50 GeoJSON.")
        results['今後30年以内に震度5強以上の地震が起こる確率'] = 'データ解析失敗'

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
        results['今後30年以内に震度6強以上の地震が起こる確率'] = _format_jshis_probability(prob_60)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching J-SHIS 60 data: {e}")
        results['今後30年以内に震度6強以上の地震が起こる確率'] = '取得失敗'
    except json.JSONDecodeError:
        print("Error decoding J-SHIS 60 GeoJSON.")
        results['今後30年以内に震度6強以上の地震が起こる確率'] = 'データ解析失敗'

    return results

def latlon_to_gsi_tile_pixel(lat: float, lon: float, zoom: int) -> tuple[int, int, int, int, int]:
    """
    緯度経度とズームレベルから地理院タイル座標(Z, X, Y)とタイル内ピクセル座標(px, py)を計算する。
    """
    n = 2 ** zoom
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)

    x_tile = int(n * ((lon + 180) / 360))
    y_tile = int(n * (1 - (math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)) / 2)

    # タイル内ピクセル座標 (0-255)
    px = int(256 * (n * ((lon + 180) / 360) - x_tile))
    py = int(256 * (n * (1 - (math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)) / 2 - y_tile))

    return zoom, x_tile, y_tile, px, py

def get_inundation_depth_from_gsi_tile(lat: float, lon: float) -> str:
    """
    国土地理院の浸水深タイル画像から想定最大浸水深を取得する。
    """
    zoom, x_tile, y_tile, px, py = latlon_to_gsi_tile_pixel(lat, lon, FLOOD_TILE_ZOOM)
    tile_url = FLOOD_TILE_URL.format(z=zoom, x=x_tile, y=y_tile)

    try:
        response = requests.get(tile_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        # 画像のピクセルデータを取得
        r, g, b, a = img.getpixel((px, py))
        pixel_rgb = (r, g, b)

        if pixel_rgb in INUNDATION_COLOR_MAP:
            return INUNDATION_COLOR_MAP[pixel_rgb]
        elif a == 0:
            return "浸水なし"
        else:
            # 該当する色がない場合、または透明度が0でないが浸水深が不明な場合
            return "情報なし"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching flood tile: {e}")
        return "対象外"
    except Exception as e:
        print(f"Error processing flood tile: {e}")
        return "処理失敗"

def get_steep_slope_info_from_gsi_tile(lat: float, lon: float) -> str:
    """
    国土地理院の急傾斜地の崩壊警戒区域タイル画像から情報を取得する。
    """
    zoom, x_tile, y_tile, px, py = latlon_to_gsi_tile_pixel(lat, lon, STEEP_SLOPE_TILE_ZOOM)
    tile_url = STEEP_SLOPE_TILE_URL.format(z=zoom, x=x_tile, y=y_tile)

    try:
        response = requests.get(tile_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        r, g, b, a = img.getpixel((px, py))
        pixel_rgb = (r, g, b)

        if pixel_rgb in STEEP_SLOPE_COLOR_MAP:
            return STEEP_SLOPE_COLOR_MAP[pixel_rgb]
        elif a == 0:
            return "該当なし"
        else:
            return "情報なし"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching steep slope tile: {e}")
        return "取得失敗"
    except Exception as e:
        print(f"Error processing steep slope tile: {e}")
        return "処理失敗"

def get_debris_flow_info_from_gsi_tile(lat: float, lon: float) -> str:
    """
    国土地理院の土石流警戒区域タイル画像から情報を取得する。
    """
    zoom, x_tile, y_tile, px, py = latlon_to_gsi_tile_pixel(lat, lon, DEBRIS_FLOW_TILE_ZOOM)
    tile_url = DEBRIS_FLOW_TILE_URL.format(z=zoom, x=x_tile, y=y_tile)

    try:
        response = requests.get(tile_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        r, g, b, a = img.getpixel((px, py))
        pixel_rgb = (r, g, b)

        if pixel_rgb in DEBRIS_FLOW_COLOR_MAP:
            return DEBRIS_FLOW_COLOR_MAP[pixel_rgb]
        elif a == 0:
            return "該当なし"
        else:
            return "情報なし"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching debris flow tile: {e}")
        return "取得失敗"
    except Exception as e:
        print(f"Error processing debris flow tile: {e}")
        return "処理失敗"

def get_landslide_info_from_gsi_tile(lat: float, lon: float) -> str:
    """
    国土地理院の地すべり警戒区域タイル画像から情報を取得する。
    """
    zoom, x_tile, y_tile, px, py = latlon_to_gsi_tile_pixel(lat, lon, LANDSLIDE_TILE_ZOOM)
    tile_url = LANDSLIDE_TILE_URL.format(z=zoom, x=x_tile, y=y_tile)

    try:
        response = requests.get(tile_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        r, g, b, a = img.getpixel((px, py))
        pixel_rgb = (r, g, b)

        if pixel_rgb in LANDSLIDE_COLOR_MAP:
            return LANDSLIDE_COLOR_MAP[pixel_rgb]
        elif a == 0:
            return "該当なし"
        else:
            return "情報なし"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching landslide tile: {e}")
        return "取得失敗"
    except Exception as e:
        print(f"Error processing landslide tile: {e}")
        return "処理失敗"
    
def get_large_scale_filled_land_info_from_geojson(lat: float, lon: float) -> str:
    """
    国土地理院の大規模盛土造成地情報をS3から取得する。
    """
    # 緯度経度から都道府県番号を計算
    pref_code = geocoding.get_pref_code(lat, lon)
    point = Point(lon, lat)

    # S3からGeoJSONファイルを取得
    s3_key = f"{S3_LARGE_FILL_LAND_FOLDER}/{S3_LARGE_FILL_LAND_FILE_PREFIX}{pref_code}.geojson"
    
    try:
        geojson = geojsonhelper.load_large_geojson(S3_LARGE_FILL_LAND_BUCKET, s3_key)
        if geojson:
            for feature in geojson["features"]:
                if shape(feature["geometry"]).contains(point):
                    return "あり"
    except Exception as e:
        print(f"Error fetching large scale filled land info: {e}")
        return "情報なし"

    return "情報なし"

def get_all_hazard_info(lat: float, lon: float) -> dict[str, str]:
    """
    すべてのハザード情報をまとめて取得する。
    """
    hazard_info = {}

    jshis_info = get_jshis_info(lat, lon)
    prob_50 = jshis_info.get('今後30年以内に震度5強以上の地震が起こる確率', 'データなし')
    prob_60 = jshis_info.get('今後30年以内に震度6強以上の地震が起こる確率', 'データなし')

    earthquake_details = []
    if prob_50 != 'データなし':
        earthquake_details.append(f"震度5強以上:{prob_50}")
    if prob_60 != 'データなし':
        earthquake_details.append(f"震度6強以上:{prob_60}")

    if earthquake_details:
        hazard_info['今後30年以内に大地震が起こる確率'] = "\n".join(earthquake_details)
    else:
        hazard_info['今後30年以内に大地震が起こる確率'] = 'データなし'

    hazard_info['想定最大浸水深'] = get_inundation_depth_from_gsi_tile(lat, lon)
    hazard_info['土砂災害警戒・特別警戒区域'] = ''
    hazard_info['津波浸水想定'] = get_tsunami_inundation_info_from_gsi_tile(lat, lon)
    hazard_info['高潮浸水想定'] = get_high_tide_inundation_info_from_gsi_tile(lat, lon)
    hazard_info['大規模盛土造成地'] = get_large_scale_filled_land_info_from_geojson(lat, lon)
    
    # 個別の土砂災害情報を取得
    debris_flow_status = get_debris_flow_info_from_gsi_tile(lat, lon)
    steep_slope_status = get_steep_slope_info_from_gsi_tile(lat, lon)
    landslide_status = get_landslide_info_from_gsi_tile(lat, lon)

    # 土砂災害警戒・特別警戒区域の統合判定と詳細リスト作成
    landslide_details = []
    consolidated_landslide_status = '該当なし'

    if debris_flow_status == '土石流特別警戒区域':
        landslide_details.append('土石流(特別警戒)')
        consolidated_landslide_status = '該当あり'
    elif debris_flow_status == '土石流警戒区域':
        landslide_details.append('土石流')
        consolidated_landslide_status = '該当あり'
    if steep_slope_status == '特別警戒区域':
        landslide_details.append('急傾斜地(特別警戒)')
        consolidated_landslide_status = '該当あり'
    elif steep_slope_status == '警戒区域':
        landslide_details.append('急傾斜地')
        consolidated_landslide_status = '該当あり'
    if landslide_status == '特別警戒区域':
        landslide_details.append('地すべり(特別警戒)')
        consolidated_landslide_status = '該当あり'
    elif landslide_status == '警戒区域':
        landslide_details.append('地すべり')
        consolidated_landslide_status = '該当あり'

    if consolidated_landslide_status == '該当あり':
        hazard_info['土砂災害警戒・特別警戒区域'] = "\n".join(landslide_details)
    else:
        hazard_info['土砂災害警戒・特別警戒区域'] = consolidated_landslide_status

    return hazard_info
