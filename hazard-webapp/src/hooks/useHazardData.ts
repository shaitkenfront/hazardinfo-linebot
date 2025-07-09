'use client';

import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchHazardInfo, fetchHazardInfoByCoordinates } from '@/utils/api';
import { HazardApiResponse, SearchState, Coordinates } from '@/types/hazard';
import { detectInputType, parseCoordinates } from '@/utils/helpers';

export function useHazardData() {
  const [searchState, setSearchState] = useState<SearchState>({
    query: '',
    type: 'address',
    isLoading: false,
    coordinates: null,
    hazardData: null,
    error: null,
  });

  // 検索クエリを実行する関数
  const searchHazardInfo = useCallback(async (query: string): Promise<HazardApiResponse> => {
    const inputType = detectInputType(query);
    
    // 緯度経度の場合は専用のAPIエンドポイントを使用
    if (inputType === 'coordinates') {
      const coords = parseCoordinates(query);
      if (coords) {
        return fetchHazardInfoByCoordinates(coords.lat, coords.lon);
      }
    }
    
    // その他の場合は柔軟な入力APIを使用
    return fetchHazardInfo(query);
  }, []);

  // React Queryを使用したデータ取得
  const {
    data: hazardData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['hazardInfo', searchState.query],
    queryFn: () => searchHazardInfo(searchState.query),
    enabled: false, // 手動で実行
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });

  // 検索を実行する関数
  const executeSearch = useCallback((query: string) => {
    const inputType = detectInputType(query);
    
    setSearchState(prev => ({
      ...prev,
      query,
      type: inputType,
      isLoading: true,
      error: null,
    }));
    
    refetch();
  }, [refetch]);

  // 座標で検索する関数（地図クリック用）
  const searchByCoordinates = useCallback((coordinates: Coordinates) => {
    const query = `${coordinates.latitude}, ${coordinates.longitude}`;
    executeSearch(query);
  }, [executeSearch]);

  // 検索状態をリセットする関数
  const resetSearch = useCallback(() => {
    setSearchState({
      query: '',
      type: 'address',
      isLoading: false,
      coordinates: null,
      hazardData: null,
      error: null,
    });
  }, []);

  // エラーをクリアする関数
  const clearError = useCallback(() => {
    setSearchState(prev => ({
      ...prev,
      error: null,
    }));
  }, []);

  // 状態を更新
  React.useEffect(() => {
    setSearchState(prev => ({
      ...prev,
      isLoading,
      hazardData: hazardData || null,
      coordinates: hazardData?.coordinates || null,
      error: error?.message || null,
    }));
  }, [hazardData, isLoading, error]);

  return {
    searchState,
    executeSearch,
    searchByCoordinates,
    resetSearch,
    clearError,
    isLoading,
    error: error?.message || null,
    hazardData,
  };
}