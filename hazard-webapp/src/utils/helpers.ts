import { SearchInputType } from '@/types/hazard';

// 入力文字列の種類を判定する関数
export function detectInputType(input: string): SearchInputType {
  const trimmedInput = input.trim();
  
  // 緯度経度の正規表現パターン
  const coordPattern = /^\s*(-?\d{1,2}(\.\d+)?)\s*,\s*(-?\d{1,3}(\.\d+)?)\s*$/;
  
  // SUUMOのURLパターン
  const suumoPattern = /^https:\/\/suumo\.jp\/(chintai|jj|ms|tochi|ikkodate|chuko|chukoikkodate|chukomansion)\//;
  
  if (coordPattern.test(trimmedInput)) {
    return 'coordinates';
  }
  
  if (suumoPattern.test(trimmedInput)) {
    return 'suumo_url';
  }
  
  return 'address';
}

// 緯度経度の文字列をパースする関数
export function parseCoordinates(input: string): { lat: number; lon: number } | null {
  const coordPattern = /^\s*(-?\d{1,2}(\.\d+)?)\s*,\s*(-?\d{1,3}(\.\d+)?)\s*$/;
  const match = input.trim().match(coordPattern);
  
  if (match) {
    const lat = parseFloat(match[1]);
    const lon = parseFloat(match[3]);
    return { lat, lon };
  }
  
  return null;
}

// 確率値を表示用にフォーマットする関数
export function formatProbability(prob: number | undefined): string {
  if (prob === undefined || prob === null) {
    return 'データなし';
  }
  return `${Math.floor(prob * 100)}%`;
}

// ハザード情報の値を表示用にフォーマットする関数
export function formatHazardValue(value: string | undefined): string {
  if (!value || value === '情報なし' || value === 'データなし') {
    return 'データなし';
  }
  return value;
}

// 地震リスクのレベルを色で表現する関数
export function getEarthquakeRiskColor(prob: number | undefined): string {
  if (!prob) return '#gray';
  
  if (prob >= 0.26) return '#d32f2f'; // 高リスク (赤)
  if (prob >= 0.06) return '#ff9800'; // 中リスク (オレンジ)
  if (prob >= 0.03) return '#fbc02d'; // やや高 (黄)
  return '#4caf50'; // 低リスク (緑)
}

// 浸水深のレベルを色で表現する関数
export function getFloodRiskColor(depth: string | undefined): string {
  if (!depth || depth === '浸水なし' || depth === 'データなし') {
    return '#4caf50'; // 緑
  }
  
  if (depth.includes('20m以上') || depth.includes('10m以上')) {
    return '#d32f2f'; // 赤
  }
  
  if (depth.includes('5m以上') || depth.includes('3m以上')) {
    return '#ff9800'; // オレンジ
  }
  
  if (depth.includes('0.5m以上') || depth.includes('1m')) {
    return '#fbc02d'; // 黄
  }
  
  return '#81c784'; // 薄緑
}

// 住所を短縮表示する関数
export function truncateAddress(address: string, maxLength: number = 30): string {
  if (address.length <= maxLength) {
    return address;
  }
  return address.substring(0, maxLength) + '...';
}