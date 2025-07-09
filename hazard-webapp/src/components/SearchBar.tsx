'use client';

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Chip,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  LocationOn as LocationIcon,
  Link as LinkIcon,
  Place as PlaceIcon
} from '@mui/icons-material';
import { detectInputType } from '@/utils/helpers';
import { SearchInputType } from '@/types/hazard';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  error?: string | null;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading = false, error }) => {
  const [query, setQuery] = useState('');
  const [inputType, setInputType] = useState<SearchInputType>('address');

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setQuery(value);
    
    // 入力内容に応じて自動的にタイプを判定
    if (value.trim()) {
      setInputType(detectInputType(value));
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query.trim());
    }
  };

  const getInputTypeInfo = (type: SearchInputType) => {
    switch (type) {
      case 'coordinates':
        return { label: '緯度経度', icon: <LocationIcon fontSize="small" />, color: 'primary' as const };
      case 'suumo_url':
        return { label: 'SUUMO URL', icon: <LinkIcon fontSize="small" />, color: 'secondary' as const };
      default:
        return { label: '住所', icon: <PlaceIcon fontSize="small" />, color: 'default' as const };
    }
  };

  const typeInfo = getInputTypeInfo(inputType);

  return (
    <Card elevation={3} sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          ハザード情報検索
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="住所、緯度経度、またはSUUMO URLを入力してください"
            value={query}
            onChange={handleInputChange}
            error={!!error}
            helperText={error}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: isLoading && (
                <InputAdornment position="end">
                  <CircularProgress size={20} />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Chip
              icon={typeInfo.icon}
              label={typeInfo.label}
              color={typeInfo.color}
              size="small"
              variant="outlined"
            />
            
            <Button
              type="submit"
              variant="contained"
              disabled={!query.trim() || isLoading}
              startIcon={<SearchIcon />}
            >
              検索
            </Button>
          </Box>
        </Box>
        
        <Typography variant="body2" color="text.secondary">
          <strong>入力例:</strong><br />
          • 住所: 東京都新宿区<br />
          • 緯度経度: 35.6586, 139.7454<br />
          • SUUMO URL: https://suumo.jp/chintai/tokyo/example
        </Typography>
      </CardContent>
    </Card>
  );
};

export default SearchBar;