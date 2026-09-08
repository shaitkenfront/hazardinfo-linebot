from app.display_formatter import format_all_hazard_info_for_display
from app.hazard_api_client import convert_api_response_to_legacy_format


def test_convert_api_response_includes_shindo_6_lower_probability():
    response = {
        'status': 'success',
        'hazard_info': {
            'jshis_prob_55': {
                'max_prob': 0.08,
                'center_prob': 0.06,
            }
        },
    }

    converted = convert_api_response_to_legacy_format(response)

    assert converted['jshis_prob_55'] == {
        'max_prob': 0.08,
        'center_prob': 0.06,
    }


def test_convert_api_response_maps_current_hazard_keys():
    response = {
        'status': 'success',
        'hazard_info': {
            'inundation_depth': {'max_info': '3m以上5m未満', 'center_info': '3m以上5m未満'},
            'tsunami_inundation': {'max_info': '1m未満', 'center_info': '1m未満'},
            'hightide_inundation': {'max_info': '0.5m未満', 'center_info': '0.5m未満'},
            'landslide_hazard': {
                'debris_flow': {'max_info': '区域内', 'center_info': '区域内'},
                'steep_slope': {'max_info': '該当なし', 'center_info': '該当なし'},
                'landslide': {'max_info': '該当なし', 'center_info': '該当なし'},
            },
        },
    }

    converted = convert_api_response_to_legacy_format(response)

    assert converted['inundation_depth']['max_info'] == '3m以上5m未満'
    assert converted['tsunami_inundation']['max_info'] == '1m未満'
    assert converted['hightide_inundation']['max_info'] == '0.5m未満'
    assert converted['landslide_hazard']['debris_flow']['max_info'] == '区域内'


def test_display_order_places_shindo_6_lower_between_5_strong_and_6_strong():
    hazards = {
        'jshis_prob_50': {'max_prob': 0.18, 'center_prob': 0.15},
        'jshis_prob_55': {'max_prob': 0.08, 'center_prob': 0.06},
        'jshis_prob_60': {'max_prob': 0.03, 'center_prob': 0.02},
    }

    display_info = format_all_hazard_info_for_display(hazards)
    earthquake_labels = list(display_info)[:3]

    assert earthquake_labels == [
        '30年以内に震度5強以上の地震が起こる確率',
        '30年以内に震度6弱以上の地震が起こる確率',
        '30年以内に震度6強以上の地震が起こる確率',
    ]
    assert display_info['30年以内に震度6弱以上の地震が起こる確率'] == (
        ' 周辺100mの最大: 8%\n 中心点: 6%'
    )
