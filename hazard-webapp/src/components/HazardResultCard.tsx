'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon,
  Water as WaterIcon,
  Landscape as LandscapeIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { HazardApiResponse } from '@/types/hazard';
import {
  formatProbability,
  formatHazardValue,
  getEarthquakeRiskColor,
  getFloodRiskColor,
  truncateAddress,
} from '@/utils/helpers';

interface HazardResultCardProps {
  data: HazardApiResponse;
}

const HazardResultCard: React.FC<HazardResultCardProps> = ({ data }) => {
  const { coordinates, source, hazard_info } = data;

  // 地震リスクの表示
  const renderEarthquakeRisk = () => {
    const prob50 = hazard_info.jshis_prob_50?.max_prob;
    const prob60 = hazard_info.jshis_prob_60?.max_prob;
    
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <WarningIcon sx={{ color: getEarthquakeRiskColor(prob50), mr: 1 }} />
            <Typography variant="h6">地震リスク</Typography>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                震度5強以上 (30年以内)
              </Typography>
              <Typography variant="h6" sx={{ color: getEarthquakeRiskColor(prob50) }}>
                {formatProbability(prob50)}
              </Typography>
              {prob50 && (
                <LinearProgress
                  variant="determinate"
                  value={prob50 * 100}
                  sx={{
                    mt: 1,
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getEarthquakeRiskColor(prob50),
                    },
                  }}
                />
              )}
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                震度6強以上 (30年以内)
              </Typography>
              <Typography variant="h6" sx={{ color: getEarthquakeRiskColor(prob60) }}>
                {formatProbability(prob60)}
              </Typography>
              {prob60 && (
                <LinearProgress
                  variant="determinate"
                  value={prob60 * 100}
                  sx={{
                    mt: 1,
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getEarthquakeRiskColor(prob60),
                    },
                  }}
                />
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // 浸水リスクの表示
  const renderFloodRisk = () => {
    const flood = hazard_info.inundation_depth?.max_info;
    const tsunami = hazard_info.tsunami_inundation?.max_info;
    const hightide = hazard_info.hightide_inundation?.max_info;
    
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <WaterIcon sx={{ color: getFloodRiskColor(flood), mr: 1 }} />
            <Typography variant="h6">浸水リスク</Typography>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                想定最大浸水深
              </Typography>
              <Chip
                label={formatHazardValue(flood)}
                sx={{
                  mt: 1,
                  backgroundColor: getFloodRiskColor(flood),
                  color: 'white',
                }}
                size="small"
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                津波浸水想定
              </Typography>
              <Chip
                label={formatHazardValue(tsunami)}
                sx={{
                  mt: 1,
                  backgroundColor: getFloodRiskColor(tsunami),
                  color: 'white',
                }}
                size="small"
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                高潮浸水想定
              </Typography>
              <Chip
                label={formatHazardValue(hightide)}
                sx={{
                  mt: 1,
                  backgroundColor: getFloodRiskColor(hightide),
                  color: 'white',
                }}
                size="small"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // 土砂災害リスクの表示
  const renderLandslideRisk = () => {
    const { debris_flow, steep_slope, landslide } = hazard_info.landslide_hazard;
    
    const hasRisk = [debris_flow, steep_slope, landslide].some(
      item => item.max_info !== '該当なし'
    );
    
    return (
      <Card variant="outlined" sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <LandscapeIcon sx={{ color: hasRisk ? '#ff9800' : '#4caf50', mr: 1 }} />
            <Typography variant="h6">土砂災害リスク</Typography>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                土石流
              </Typography>
              <Chip
                label={debris_flow.max_info}
                color={debris_flow.max_info !== '該当なし' ? 'warning' : 'success'}
                size="small"
                sx={{ mt: 1 }}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                急傾斜地
              </Typography>
              <Chip
                label={steep_slope.max_info}
                color={steep_slope.max_info !== '該当なし' ? 'warning' : 'success'}
                size="small"
                sx={{ mt: 1 }}
              />
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                地すべり
              </Typography>
              <Chip
                label={landslide.max_info}
                color={landslide.max_info !== '該当なし' ? 'warning' : 'success'}
                size="small"
                sx={{ mt: 1 }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  // その他のリスクの表示
  const renderOtherRisk = () => {
    const largeFillLand = hazard_info.large_fill_land?.max_info;
    
    return (
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <HomeIcon sx={{ mr: 1 }} />
            <Typography variant="h6">その他のリスク</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" color="text.secondary">
            大規模盛土造成地
          </Typography>
          <Chip
            label={formatHazardValue(largeFillLand)}
            color={largeFillLand === 'あり' ? 'warning' : 'success'}
            size="small"
            sx={{ mt: 1 }}
          />
        </AccordionDetails>
      </Accordion>
    );
  };

  return (
    <Box>
      {/* 検索結果の基本情報 */}
      <Card elevation={3} sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            ハザード情報
          </Typography>
          
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {truncateAddress(source)}
          </Typography>
          
          <Typography variant="body2" color="text.secondary">
            座標: {coordinates.latitude.toFixed(4)}, {coordinates.longitude.toFixed(4)}
          </Typography>
          
          {hazard_info.property_address && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              物件住所: {hazard_info.property_address}
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* ハザード情報の表示 */}
      {renderEarthquakeRisk()}
      {renderFloodRisk()}
      {renderLandslideRisk()}
      {renderOtherRisk()}
    </Box>
  );
};

export default HazardResultCard;