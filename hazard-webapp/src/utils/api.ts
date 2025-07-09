import axios from 'axios';
import { HazardApiResponse, HazardApiError } from '@/types/hazard';

// API設定
const API_BASE_URL = process.env.HAZARD_API_URL || 'https://your-api-gateway-url.com';

export const hazardApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ハザード情報を取得する関数
export async function fetchHazardInfo(input: string): Promise<HazardApiResponse> {
  try {
    const response = await hazardApi.post<HazardApiResponse>('/hazard-info', {
      input: input,
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const errorData = error.response.data as HazardApiError;
      throw new Error(errorData.message || 'ハザード情報の取得に失敗しました');
    }
    throw new Error('ネットワークエラーが発生しました');
  }
}

// 座標からハザード情報を取得する関数（後方互換性用）
export async function fetchHazardInfoByCoordinates(
  lat: number,
  lon: number
): Promise<HazardApiResponse> {
  try {
    const response = await hazardApi.get<HazardApiResponse>('/hazard-info', {
      params: { lat, lon },
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const errorData = error.response.data as HazardApiError;
      throw new Error(errorData.message || 'ハザード情報の取得に失敗しました');
    }
    throw new Error('ネットワークエラーが発生しました');
  }
}