'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { CircularProgress, Box } from '@mui/material';
import { Coordinates } from '@/types/hazard';

// 地図コンポーネントを動的インポート（SSR対応）
const HazardMap = dynamic(() => import('./HazardMap'), {
  ssr: false,
  loading: () => (
    <Box
      sx={{
        height: 400,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.100',
        borderRadius: 1,
      }}
    >
      <CircularProgress />
    </Box>
  ),
});

interface MapWrapperProps {
  center?: Coordinates;
  onLocationSelect?: (coordinates: Coordinates) => void;
  markers?: Array<{
    position: Coordinates;
    popup?: string;
  }>;
  height?: number | string;
}

const MapWrapper: React.FC<MapWrapperProps> = (props) => {
  return <HazardMap {...props} />;
};

export default MapWrapper;