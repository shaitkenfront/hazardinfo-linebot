import pytest
from src.app.hazard_info import _format_hazard_output_string, _format_jshis_probability, _get_points_in_radius

def test_format_hazard_output_string_basic_case():
    max_val = "20m以上"
    center_val = "5m以上10mm未満"
    expected = "周辺100mの最大: 20m以上\n中心点: 5m以上10m未満"
    assert _format_hazard_output_string(max_val, center_val) == expected

def test_format_hazard_output_string_same_value():
    max_val = "1m未満"
    center_val = "1m未満"
    expected = "周辺100mの最大: 1m未満\n中心点: 1m未満"
    assert _format_hazard_output_string(max_val, center_val) == expected

def test_format_hazard_output_string_no_max_val():
    max_val = None
    center_val = "0.5m未満"
    expected = "周辺100mの最大: データなし\n中心点: 0.5m未満"
    assert _format_hazard_output_string(max_val, center_val) == expected

def test_format_hazard_output_string_no_center_val():
    max_val = "3m以上"
    center_val = None
    expected = "周辺100mの最大: 3m以上\n中心点: データなし"
    assert _format_hazard_output_string(max_val, center_val) == expected

def test_format_hazard_output_string_no_data():
    max_val = None
    center_val = None
    expected = "データなし"
    assert _format_hazard_output_string(max_val, center_val) == expected

def test_format_hazard_output_string_custom_no_data_str():
    max_val = None
    center_val = None
    expected = "情報なし"
    assert _format_hazard_output_string(max_val, center_val, no_data_str="情報なし") == expected

    max_val = "あり"
    center_val = None
    expected = "周辺100mの最大: あり\n中心点: 情報なし"
    assert _format_hazard_output_string(max_val, center_val, no_data_str="情報なし") == expected


def test_format_jshis_probability_valid_float():
    assert _format_jshis_probability(0.123) == "12%"
    assert _format_jshis_probability(0.0) == "0%"
    assert _format_jshis_probability(0.999) == "99%"

def test_format_jshis_probability_none():
    assert _format_jshis_probability(None) == "データなし"

def test_format_jshis_probability_invalid_string():
    assert _format_jshis_probability("abc") == "データ解析失敗"

def test_get_points_in_radius_basic():
    lat, lon = 35.0, 135.0
    radius_m = 100
    num_points = 8
    points = _get_points_in_radius(lat, lon, radius_m, num_points)
    assert len(points) == num_points + 1  # 中心点 + num_points
    assert points[0] == (lat, lon)  # 中心点が正しいことを確認

def test_get_points_in_radius_zero_radius():
    lat, lon = 35.0, 135.0
    radius_m = 0
    num_points = 8
    points = _get_points_in_radius(lat, lon, radius_m, num_points)
    assert len(points) == 1
    assert points[0] == (lat, lon)

def test_get_points_in_radius_num_points():
    lat, lon = 35.0, 135.0
    radius_m = 50
    num_points = 4
    points = _get_points_in_radius(lat, lon, radius_m, num_points)
    assert len(points) == num_points + 1


