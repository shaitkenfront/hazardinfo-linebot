import os
import requests

# 環境変数からAPIキーを取得
API_KEY = os.environ.get('GOOGLE_API_KEY')

GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def geocode(address: str) -> tuple[float, float] | None:
    """
    住所文字列を緯度・経度に変換する（ジオコーディング）。

    Args:
        address: 日本語の住所文字列。

    Returns:
        tuple[float, float] | None: (緯度, 経度) のタプル。変換失敗時はNone。
    """
    if not API_KEY:
        print("Google Geocoding API key is not configured.")
        return None

    params = {
        'address': address,
        'key': API_KEY,
        'language': 'ja'
    }
    
    try:
        response = requests.get(GEOCODING_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding API Error: {data['status']}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling Geocoding API: {e}")
        return None

def reverse_geocode(lat: float, lon: float) -> str | None:
    """
    緯度・経度を住所文字列に変換する（逆ジオコーディング）。

    Args:
        lat: 緯度。
        lon: 経度。

    Returns:
        str | None: 住所文字列。変換失敗時はNone。
    """
    if not API_KEY:
        print("Google Geocoding API key is not configured.")
        return None

    params = {
        'latlng': f'{lat},{lon}',
        'key': API_KEY,
        'language': 'ja'
    }

    try:
        response = requests.get(GEOCODING_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK':
            # 最も適切と思われる住所を返す
            return data['results'][0]['formatted_address']
        else:
            print(f"Reverse Geocoding API Error: {data['status']}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error calling Reverse Geocoding API: {e}")
        return None