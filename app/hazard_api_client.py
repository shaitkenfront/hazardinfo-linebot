import os
import requests
from typing import Dict, Optional, List


class HazardAPIClient:
    """
    外部のハザード情報REST APIクライアント。
    HazardInfo_RESTAPI.mdで定義された仕様に基づいてハザード情報を取得する。
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Args:
            api_url: ハザード情報APIのベースURL。Noneの場合は環境変数HAZARD_MAP_API_URLから取得。
        """
        self.api_url = api_url or os.environ.get('HAZARD_MAP_API_URL')
        self.api_key = os.environ.get('HAZARD_MAP_API_KEY')
        if not self.api_url:
            raise ValueError("API URL is required. Set HAZARD_MAP_API_URL environment variable or pass api_url parameter.")

    def _make_request(self, params: Dict) -> Dict:
        """
        APIへのリクエストを送信する共通メソッド。
        """
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key

        try:
            response = requests.get(self.api_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching hazard info from API: {e}")
            return self._get_error_response(str(e))

    def _get_default_hazard_types(self) -> List[str]:
        """
        デフォルトで取得するすべてのハザードタイプのリストを返す。
        
        Returns:
            有効なハザードタイプリスト
        """
        return [
            'earthquake', 
            'flood', 
            'flood_keizoku', 
            'kaokutoukai_hanran',
            'tsunami', 
            'high_tide', 
            'landslide', 
            'avalanche',
            'large_fill_land'
        ]

    def get_hazard_info(
        self, 
        lat: float, 
        lon: float, 
        datum: str = 'wgs84',
        hazard_types: Optional[List[str]] = None
    ) -> Dict:
        """
        指定された座標のハザード情報を取得する。
        
        Args:
            lat: 緯度
            lon: 経度  
            datum: 座標系 ('wgs84' または 'tokyo')
            hazard_types: 取得するハザード情報のタイプリスト。Noneの場合はデフォルトリストを使用。
                         利用可能: earthquake, flood, flood_keizoku, kaokutoukai_hanran, tsunami, high_tide, landslide, avalanche, large_fill_land
        
        Returns:
            APIからのレスポンス辞書
        """
        params = {
            'lat': lat,
            'lon': lon,
            'datum': datum
        }
        
        if hazard_types is None:
            hazard_types = self._get_default_hazard_types()
        
        if hazard_types:
            params['hazard_types'] = ','.join(hazard_types)
        
        return self._make_request(params)
    
    def get_hazard_info_by_input(
        self, 
        input_text: str, 
        datum: str = 'wgs84',
        hazard_types: Optional[List[str]] = None
    ) -> Dict:
        """
        住所または座標文字列からハザード情報を取得する。
        
        Args:
            input_text: 住所または緯度経度の文字列
            datum: 座標系 ('wgs84' または 'tokyo')
            hazard_types: 取得するハザード情報のタイプリスト。Noneの場合はデフォルトリストを使用。
        
        Returns:
            APIからのレスポンス辞書
        """
        params = {
            'input': input_text,
            'datum': datum
        }
        
        if hazard_types is None:
            hazard_types = self._get_default_hazard_types()
        
        if hazard_types:
            params['hazard_types'] = ','.join(hazard_types)
        
        return self._make_request(params)
    
    def _get_error_response(self, error_message: str) -> Dict:
        """
        エラー時のレスポンスフォーマットを統一する。
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            エラー情報を含む辞書
        """
        return {
            'status': 'error',
            'error_message': error_message,
            'coordinates': None,
            'hazard_info': {}
        }


def convert_api_response_to_legacy_format(api_response: Dict) -> Dict:
    """
    REST APIのレスポンスを既存のhazard_info.pyのフォーマットに変換する。
    
    Args:
        api_response: REST APIからのレスポンス
        
    Returns:
        既存フォーマットに変換されたハザード情報
    """
    if api_response.get('status') == 'error':
        return {}
    
    hazard_info = api_response.get('hazard_info', {})
    legacy_format = {}
    
    # 地震発生確率の変換
    jshis_50 = hazard_info.get('jshis_prob_50', {})
    if jshis_50:
        legacy_format['jshis_prob_50'] = {
            'max_prob': jshis_50.get('max_prob'),
            'center_prob': jshis_50.get('center_prob')
        }
    
    jshis_60 = hazard_info.get('jshis_prob_60', {})
    if jshis_60:
        legacy_format['jshis_prob_60'] = {
            'max_prob': jshis_60.get('max_prob'),
            'center_prob': jshis_60.get('center_prob')
        }
    
    # 浸水深情報の変換 (APIレスポンスキー: flood -> 旧キー: inundation_depth)
    flood = hazard_info.get('flood', {})
    if flood:
        legacy_format['inundation_depth'] = {
            'max_info': flood.get('max_info'),
            'center_info': flood.get('center_info')
        }
    
    # 浸水継続時間の変換
    flood_keizoku = hazard_info.get('flood_keizoku', {})
    if flood_keizoku:
        legacy_format['flood_keizoku'] = {
            'max_info': flood_keizoku.get('max_info'),
            'center_info': flood_keizoku.get('center_info')
        }

    # 家屋倒壊等氾濫想定区域の変換
    kaokutoukai = hazard_info.get('kaokutoukai_hanran', {})
    if kaokutoukai:
        legacy_format['kaokutoukai_hanran'] = {
            'max_info': kaokutoukai.get('max_info'),
            'center_info': kaokutoukai.get('center_info')
        }

    # 津波浸水想定の変換 (APIレスポンスキー: tsunami -> 旧キー: tsunami_inundation)
    tsunami = hazard_info.get('tsunami', {})
    if tsunami:
        legacy_format['tsunami_inundation'] = {
            'max_info': tsunami.get('max_info'),
            'center_info': tsunami.get('center_info')
        }
    
    # 高潮浸水想定の変換 (APIレスポンスキー: high_tide -> 旧キー: hightide_inundation)
    high_tide = hazard_info.get('high_tide', {})
    if high_tide:
        legacy_format['hightide_inundation'] = {
            'max_info': high_tide.get('max_info'),
            'center_info': high_tide.get('center_info')
        }
    
    # 大規模盛土造成地の変換
    large_fill = hazard_info.get('large_fill_land', {})
    if large_fill:
        legacy_format['large_fill_land'] = {
            'max_info': large_fill.get('max_info'),
            'center_info': large_fill.get('center_info')
        }
    
    # 土砂災害情報の変換 (APIレスポンスキー: landslide -> 旧キー: landslide_hazard)
    landslide = hazard_info.get('landslide', {})
    if landslide:
        legacy_format['landslide_hazard'] = {
            'debris_flow': {
                'max_info': landslide.get('debris_flow', {}).get('max_info'),
                'center_info': landslide.get('debris_flow', {}).get('center_info')
            },
            'steep_slope': {
                'max_info': landslide.get('steep_slope', {}).get('max_info'),
                'center_info': landslide.get('steep_slope', {}).get('center_info')
            },
            'landslide': {
                'max_info': landslide.get('landslide', {}).get('max_info'),
                'center_info': landslide.get('landslide', {}).get('center_info')
            }
        }
    
    # 雪崩危険箇所の変換
    avalanche = hazard_info.get('avalanche', {})
    if avalanche:
        legacy_format['avalanche'] = {
            'max_info': avalanche.get('max_info'),
            'center_info': avalanche.get('center_info')
        }
    
    return legacy_format