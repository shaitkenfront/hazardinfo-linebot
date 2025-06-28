import re

# 緯度経度の正規表現パターン（例: 35.6586, 139.7454）
LATLON_PATTERN = re.compile(r'^\s*(-?\d{1,2}(\.\d+)?)\s*,\s*(-?\d{1,3}(\.\d+)?)\s*$')

# SUUMO物件詳細URLの正規表現パターン
SUUMO_URL_PATTERN = re.compile(r'^https://suumo\.jp/(chintai|jj|ms|tochi|kodate|chuko|chukomansion)/.*/bc_.*$')

def parse_input_type(text: str) -> tuple[str, str]:
    """
    ユーザーの入力テキストを解析し、タイプと値を返す。

    Args:
        text: ユーザーからの入力文字列。

    Returns:
        (str, str): 入力のタイプ（'latlon', 'suumo_url', 'address'）と元のテキストのタプル。
    """
    if LATLON_PATTERN.match(text):
        return 'latlon', text
    
    if SUUMO_URL_PATTERN.match(text):
        return 'suumo_url', text
        
    return 'address', text
