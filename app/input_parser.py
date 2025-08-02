import re

# 緯度経度の正規表現パターン（例: 35.6586, 139.7454）
LATLON_PATTERN = re.compile(r'^\s*(-?\d{1,2}(\.\d+)?)\s*,\s*(-?\d{1,3}(\.\d+)?)\s*$')

OTHER_URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')

def parse_input_type(text: str) -> tuple[str, str]:
    """
    ユーザーの入力テキストを解析し、タイプと値を返す。

    Args:
        text: ユーザーからの入力文字列。

    Returns:
        (str, str): 入力のタイプ（'latlon', 'address', 'invalid_url'）と元のテキストのタプル。
    """
    if LATLON_PATTERN.match(text):
        return 'latlon', text
        
    if OTHER_URL_PATTERN.match(text):
        return 'invalid_url', text

    return 'address', text
