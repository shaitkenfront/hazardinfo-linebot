import pytest
from unittest.mock import patch, Mock
from src.app.suumo_scraper import extract_address_from_suumo

# モック用のHTMLコンテンツ
HTML_TH_TD_P = """
<html><body><table><tr><th>住所</th><td><p>東京都港区</p></td></tr></table></body></html>
"""

HTML_SPAN_SPAN = """
<html><body><span>所在地</span><span>大阪府大阪市</span></body></html>
"""

HTML_DIV_CLASS = """
<html><body><div class="property_view_note-info-address">神奈川県横浜市</div></body></html>
"""

HTML_NO_ADDRESS = """
<html><body><div>住所なし</div></body></html>
"""

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get

def test_extract_address_from_suumo_th_td_p(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, content=HTML_TH_TD_P)
    address = extract_address_from_suumo("http://example.com/suumo")
    assert address == "東京都港区"

def test_extract_address_from_suumo_span_span(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, content=HTML_SPAN_SPAN)
    address = extract_address_from_suumo("http://example.com/suumo")
    assert address == "大阪府大阪市"

def test_extract_address_from_suumo_div_class(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, content=HTML_DIV_CLASS)
    address = extract_address_from_suumo("http://example.com/suumo")
    assert address == "神奈川県横浜市"

def test_extract_address_from_suumo_no_address(mock_requests_get):
    mock_requests_get.return_value = Mock(status_code=200, content=HTML_NO_ADDRESS)
    address = extract_address_from_suumo("http://example.com/suumo")
    assert address is None

def test_extract_address_from_suumo_request_error(mock_requests_get):
    mock_requests_get.side_effect = requests.exceptions.RequestException("Connection error")
    address = extract_address_from_suumo("http://example.com/suumo")
    assert address is None
