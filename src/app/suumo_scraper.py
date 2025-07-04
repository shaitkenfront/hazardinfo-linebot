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
        
        # ルール: thが「住所」または「所在地」である次のtdセルの最初のpタグの内容
        print(f"All th tags found: {[span.text.strip() for span in soup.find_all('th')]}")  # デバッグ用
        for th_tag in soup.find_all('th'):
            if th_tag.text.strip() in ['住所', '所在地']:
                td_tag = th_tag.find_next_sibling('td')
                print(f"Found td tag: {td_tag}")
                if td_tag:
                    p_tag = td_tag.find('p')
                    if p_tag:
                        return p_tag.text.strip()
                    else:
                        return td_tag.text.strip()
        

        # 既存のセレクタ（フォールバック）
        address_element = soup.find('div', class_='property_view_note-info-address')
        if address_element:
            return address_element.text.strip()
        
        address_element = soup.select_one('.property_view_note-info-address') # CSSセレクタで検索
        if address_element:
            return address_element.text.strip()

        return None # 住所が見つからない場合

    except requests.exceptions.RequestException as e:
        print(f"Error fetching SUUMO URL: {e}")
        return None
