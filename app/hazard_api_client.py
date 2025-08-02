import os
import requests
import json
from typing import Dict, Optional, List, Union


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
        if not self.api_url:
            raise ValueError("API URL is required. Set HAZARD_MAP_API_URL environment variable or pass api_url parameter.")
    
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
            hazard_types: 取得するハザード情報のタイプリスト。Noneの場合は全て取得。
                         利用可能: earthquake, flood, tsunami, high_tide, large_fill_land, landslide
        
        Returns:
            APIからのレスポンス辞書
        """
        params = {
            'lat': lat,
            'lon': lon,
            'datum': datum
        }
        
        if hazard_types:
            params['hazard_types'] = ','.join(hazard_types)
        
        try:
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching hazard info from API: {e}")
            return self._get_error_response(str(e))
    
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
            hazard_types: 取得するハザード情報のタイプリスト
        
        Returns:
            APIからのレスポンス辞書
        """
        params = {
            'input': input_text,
            'datum': datum
        }
        
        if hazard_types:
            params['hazard_types'] = ','.join(hazard_types)
        
        try:
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching hazard info from API: {e}")
            return self._get_error_response(str(e))
    
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
    
    # 浸水深情報の変換
    inundation = hazard_info.get('inundation_depth', {})
    if inundation:
        legacy_format['inundation_depth'] = {
            'max_info': inundation.get('max_info'),
            'center_info': inundation.get('center_info')
        }
    
    # 津波浸水想定の変換
    tsunami = hazard_info.get('tsunami_inundation', {})
    if tsunami:
        legacy_format['tsunami_inundation'] = {
            'max_info': tsunami.get('max_info'),
            'center_info': tsunami.get('center_info')
        }
    
    # 高潮浸水想定の変換
    high_tide = hazard_info.get('hightide_inundation', {})
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
    
    # 土砂災害情報の変換
    landslide = hazard_info.get('landslide_hazard', {})
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
    
    return legacy_format