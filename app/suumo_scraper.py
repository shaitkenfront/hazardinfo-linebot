import requests
from bs4 import BeautifulSoup

def extract_address_from_suumo(url: str) -> str | None:
    """
    SUUMOの物件詳細ページURLから住所を抽出する。

    Args:
        url: SUUMOの物件詳細URL。

    Returns:
        str | None: 抽出した住所文字列。見つからない場合はNone。
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # SUUMOの住所は'ui-text--bold'クラスを持つdivに含まれることが多い
        # より特定しやすいセレクタやIDがあればそちらを優先する
        # 例：<div class="property_view_note-info-address">...</div>など
        address_element = soup.find('div', class_='property_view_note-info-address')

        if address_element:
            return address_element.text.strip()
        
        # 代替セレクタ（サイト構造の変更に対応）
        address_element = soup.select_one('.property_view_note-info-address') # CSSセレクタで検索
        if address_element:
            return address_element.text.strip()

        return None # 住所が見つからない場合

    except requests.exceptions.RequestException as e:
        print(f"Error fetching SUUMO URL: {e}")
        return None
