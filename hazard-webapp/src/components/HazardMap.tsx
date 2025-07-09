'use client';

import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import { LatLngExpression, Icon } from 'leaflet';
import { Box, Paper, Typography } from '@mui/material';
import { Coordinates } from '@/types/hazard';

// Leafletアイコンの設定
const defaultIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface HazardMapProps {
  center?: Coordinates;
  onLocationSelect?: (coordinates: Coordinates) => void;
  markers?: Array<{
    position: Coordinates;
    popup?: string;
  }>;
  height?: number | string;
}

// 地図クリックイベントを処理するコンポーネント
const MapClickHandler: React.FC<{ onLocationSelect?: (coordinates: Coordinates) => void }> = ({
  onLocationSelect,
}) => {
  useMapEvents({
    click(e) {
      if (onLocationSelect) {
        onLocationSelect({
          latitude: e.latlng.lat,
          longitude: e.latlng.lng,
        });
      }
    },
  });
  return null;
};

const HazardMap: React.FC<HazardMapProps> = ({
  center = { latitude: 35.6762, longitude: 139.6503 }, // 東京都庁
  onLocationSelect,
  markers = [],
  height = 400,
}) => {
  const mapRef = useRef(null);

  // マーカーが変更された時に地図の中心を更新
  useEffect(() => {
    if (markers.length > 0 && mapRef.current) {
      const map = mapRef.current;
      const lastMarker = markers[markers.length - 1];
      map.setView([lastMarker.position.latitude, lastMarker.position.longitude], 15);
    }
  }, [markers]);

  const mapCenter: LatLngExpression = [center.latitude, center.longitude];

  return (
    <Paper elevation={3} sx={{ overflow: 'hidden' }}>
      <Box sx={{ height: height, position: 'relative' }}>
        <MapContainer
          center={mapCenter}
          zoom={10}
          style={{ height: '100%', width: '100%' }}
          ref={mapRef}
        >
          {/* 地理院標準地図タイル */}
          <TileLayer
            attribution='&copy; <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>'
            url="https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png"
          />
          
          {/* OpenStreetMapタイル（フォールバック） */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            opacity={0}
          />

          {/* 地図クリックハンドラー */}
          <MapClickHandler onLocationSelect={onLocationSelect} />

          {/* マーカーの表示 */}
          {markers.map((marker, index) => (
            <Marker
              key={index}
              position={[marker.position.latitude, marker.position.longitude]}
              icon={defaultIcon}
            >
              {marker.popup && (
                <Popup>
                  <Typography variant="body2">
                    {marker.popup}
                  </Typography>
                </Popup>
              )}
            </Marker>
          ))}
        </MapContainer>

        {/* 地図の操作説明 */}
        <Box
          sx={{
            position: 'absolute',
            top: 10,
            right: 10,
            bgcolor: 'background.paper',
            p: 1,
            borderRadius: 1,
            boxShadow: 1,
            zIndex: 1000,
          }}
        >
          <Typography variant="caption" color="text.secondary">
            地図をクリックして位置を選択
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default HazardMap;