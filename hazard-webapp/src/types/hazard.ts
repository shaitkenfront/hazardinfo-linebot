// ハザード情報の型定義
export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface HazardDataItem {
  max_prob?: number;
  center_prob?: number;
  max_info?: string;
  center_info?: string;
}

export interface LandslideHazardDetail {
  max_info: string;
  center_info: string;
}

export interface LandslideHazard {
  debris_flow: LandslideHazardDetail;
  steep_slope: LandslideHazardDetail;
  landslide: LandslideHazardDetail;
}

export interface HazardInfo {
  jshis_prob_50: HazardDataItem;
  jshis_prob_60: HazardDataItem;
  inundation_depth: HazardDataItem;
  tsunami_inundation: HazardDataItem;
  hightide_inundation: HazardDataItem;
  large_fill_land: HazardDataItem;
  landslide_hazard: LandslideHazard;
  property_address?: string;
}

export interface HazardApiResponse {
  coordinates: Coordinates;
  source: string;
  input_type: 'address' | 'latlon' | 'suumo_url';
  hazard_info: HazardInfo;
  status: 'success';
}

export interface HazardApiError {
  error: string;
  message: string;
}

// 検索に関する型
export type SearchInputType = 'address' | 'coordinates' | 'suumo_url';

export interface SearchState {
  query: string;
  type: SearchInputType;
  isLoading: boolean;
  coordinates: Coordinates | null;
  hazardData: HazardApiResponse | null;
  error: string | null;
}