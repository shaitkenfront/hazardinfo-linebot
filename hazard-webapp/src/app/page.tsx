'use client';

import React from 'react';
import {
  Container,
  Grid,
  Typography,
  AppBar,
  Toolbar,
  Box,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Map as MapIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import SearchBar from '@/components/SearchBar';
import MapWrapper from '@/components/MapWrapper';
import HazardResultCard from '@/components/HazardResultCard';
import { useHazardData } from '@/hooks/useHazardData';

export default function HomePage() {
  const {
    searchState,
    executeSearch,
    searchByCoordinates,
    clearError,
    isLoading,
    error,
    hazardData,
  } = useHazardData();

  // 地図上でクリックされた時の処理
  const handleMapClick = (coordinates: { latitude: number; longitude: number }) => {
    searchByCoordinates(coordinates);
  };

  // 検索バーから検索された時の処理
  const handleSearch = (query: string) => {
    executeSearch(query);
  };

  // マーカーの生成
  const markers = hazardData ? [
    {
      position: hazardData.coordinates,
      popup: `${hazardData.source}\n座標: ${hazardData.coordinates.latitude.toFixed(4)}, ${hazardData.coordinates.longitude.toFixed(4)}`,
    },
  ] : [];

  return (
    <>
      {/* ヘッダー */}
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <MapIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            ハザードマップ情報検索
          </Typography>
          <InfoIcon />
        </Toolbar>
      </AppBar>

      {/* メインコンテンツ */}
      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Grid container spacing={3}>
          {/* 左側: 検索とメイン情報 */}
          <Grid item xs={12} lg={6}>
            {/* 検索バー */}
            <SearchBar
              onSearch={handleSearch}
              isLoading={isLoading}
              error={error}
            />

            {/* ハザード情報表示 */}
            {hazardData && (
              <Box sx={{ mt: 2 }}>
                <HazardResultCard data={hazardData} />
              </Box>
            )}

            {/* 初期状態のメッセージ */}
            {!hazardData && !isLoading && (
              <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  ハザード情報を検索
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  住所、緯度経度、またはSUUMO URLを入力するか、<br />
                  地図上をクリックして位置を選択してください。
                </Typography>
              </Box>
            )}
          </Grid>

          {/* 右側: 地図 */}
          <Grid item xs={12} lg={6}>
            <Box sx={{ position: 'sticky', top: 20 }}>
              <Typography variant="h6" gutterBottom>
                地図
              </Typography>
              <MapWrapper
                center={hazardData?.coordinates}
                onLocationSelect={handleMapClick}
                markers={markers}
                height={600}
              />
              
              {/* 地図の説明 */}
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  <strong>使い方:</strong><br />
                  • 地図をクリックしてその位置のハザード情報を検索<br />
                  • 検索結果の位置が地図上にマーカーで表示されます<br />
                  • 地図は国土地理院の標準地図を使用しています
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* エラー通知 */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={clearError}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={clearError} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </>
  );
}