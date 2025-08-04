import math
from typing import Dict, Any, Optional


def _format_jshis_probability(prob_value: Optional[float]) -> str:
    """
    J-SHISから取得した確率値をフォーマットする。
    Noneの場合や解析エラーの場合は「データなし」を返す。
    """
    if prob_value is not None:
        try:
            prob_float = float(prob_value)
            return f"{math.floor(prob_float * 100)}%"
        except (ValueError, TypeError):
            return 'データ解析失敗'
    return 'データなし'


def _format_hazard_output_string(max_val: Any, center_val: Any, no_data_str: str = 'データなし') -> str:
    """
    ハザード情報の最大値と中心点の値をフォーマットして返す。
    max_val, center_valは既にフォーマット済みの文字列、またはNone/データなし相当の値。
    """
    # max_valとcenter_valがNoneの場合を考慮
    max_val_display = max_val if max_val is not None else no_data_str
    center_val_display = center_val if center_val is not None else no_data_str

    if max_val_display == no_data_str and center_val_display == no_data_str:
        return no_data_str
    
    # 常に2行形式で出力
    return f" 周辺100mの最大: {max_val_display}\n 中心点: {center_val_display}"


def format_all_hazard_info_for_display(hazards: Dict[str, Any]) -> Dict[str, str]:
    """
    REST APIから取得したハザードデータを表示用に整形する。
    """
    display_info = {}

    # 地震発生確率
    prob_50_data = hazards.get('jshis_prob_50', {})
    prob_50_str = _format_hazard_output_string(
        _format_jshis_probability(prob_50_data.get('max_prob')),
        _format_jshis_probability(prob_50_data.get('center_prob'))
    )
    display_info['30年以内に震度5強以上の地震が起こる確率'] = prob_50_str

    prob_60_data = hazards.get('jshis_prob_60', {})
    prob_60_str = _format_hazard_output_string(
        _format_jshis_probability(prob_60_data.get('max_prob')),
        _format_jshis_probability(prob_60_data.get('center_prob'))
    )
    display_info['30年以内に震度6強以上の地震が起こる確率'] = prob_60_str

    # 想定最大浸水深
    inundation_data = hazards.get('inundation_depth', {})
    display_info['想定最大浸水深'] = _format_hazard_output_string(
        inundation_data.get('max_info'),
        inundation_data.get('center_info'),
        no_data_str="浸水なし"
    )

    # 津波浸水想定
    tsunami_data = hazards.get('tsunami_inundation', {})
    display_info['津波浸水想定'] = _format_hazard_output_string(
        tsunami_data.get('max_info'),
        tsunami_data.get('center_info'),
        no_data_str="浸水想定なし"
    )

    # 高潮浸水想定
    hightide_data = hazards.get('hightide_inundation', {})
    display_info['高潮浸水想定'] = _format_hazard_output_string(
        hightide_data.get('max_info'),
        hightide_data.get('center_info'),
        no_data_str="浸水想定なし"
    )

    # 大規模盛土造成地
    large_fill_land_data = hazards.get('large_fill_land', {})
    if large_fill_land_data and large_fill_land_data.get("overlapped") is not None:
        display_info['大規模盛土造成地'] = _format_hazard_output_string(
            large_fill_land_data.get("max_info"),
            large_fill_land_data.get("center_info"),
            no_data_str="該当なし")


    # 土砂災害警戒・特別警戒区域
    landslide_hazard_data = hazards.get('landslide_hazard', {})
    max_landslide_descriptions = []
    center_landslide_descriptions = []

    # 土石流
    debris_flow_data = landslide_hazard_data.get('debris_flow', {})
    if debris_flow_data.get('max_info') and debris_flow_data.get('max_info') != '該当なし':
        max_landslide_descriptions.append(debris_flow_data['max_info'])
    if debris_flow_data.get('center_info') and debris_flow_data.get('center_info') != '該当なし':
        center_landslide_descriptions.append(debris_flow_data['center_info'])

    # 急傾斜地
    steep_slope_data = landslide_hazard_data.get('steep_slope', {})
    if steep_slope_data.get('max_info') and steep_slope_data.get('max_info') != '該当なし':
        max_landslide_descriptions.append(steep_slope_data['max_info'])
    if steep_slope_data.get('center_info') and steep_slope_data.get('center_info') != '該当なし':
        center_landslide_descriptions.append(steep_slope_data['center_info'])

    # 地すべり
    landslide_data = landslide_hazard_data.get('landslide', {})
    if landslide_data.get('max_info') and landslide_data.get('max_info') != '該当なし':
        max_landslide_descriptions.append(landslide_data['max_info'])
    if landslide_data.get('center_info') and landslide_data.get('center_info') != '該当なし':
        center_landslide_descriptions.append(landslide_data['center_info'])

    max_landslide_str = ", ".join(max_landslide_descriptions) if max_landslide_descriptions else "該当なし"
    center_landslide_str = ", ".join(center_landslide_descriptions) if center_landslide_descriptions else "該当なし"

    display_info['土砂災害警戒・特別警戒区域'] = _format_hazard_output_string(max_landslide_str, center_landslide_str, "該当なし")

    return display_info