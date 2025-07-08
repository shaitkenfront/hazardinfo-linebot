# ハザードマップ情報API

住所、URL、緯度経度を受け取ってハザードマップ情報をJSONで返すLambda関数です。

## ファイル

- `hazard_api_function.py` - REST API用のLambda関数

## API仕様

### エンドポイント

`POST/GET /hazard-info`

### リクエスト方法

#### 方法1: 柔軟な入力（推奨）

**GET リクエスト (クエリパラメータ)**
```bash
# 住所で検索
GET /hazard-info?input=東京都新宿区

# 緯度経度で検索
GET /hazard-info?input=35.6586,139.7454

# SUUMO URLで検索
GET /hazard-info?input=https://suumo.jp/chintai/tokyo/example
```

**POST リクエスト (JSON)**
```json
{
  "input": "東京都新宿区"
}
```

#### 方法2: 従来の緯度経度指定（後方互換性）

**GET リクエスト**
```
GET /hazard-info?lat=35.6586&lon=139.7454
```

**POST リクエスト**
```json
{
  "lat": 35.6586,
  "lon": 139.7454
}
```

### パラメータ

#### 柔軟な入力
- `input` (必須): 以下のいずれかの形式
  - 住所（例: "東京都新宿区"）
  - 緯度経度（例: "35.6586, 139.7454"）
  - SUUMO URL（例: "https://suumo.jp/chintai/tokyo/example"）

#### 従来の緯度経度指定
- `lat` (必須): 緯度 (24.0〜46.0の範囲)
- `lon` (必須): 経度 (123.0〜146.0の範囲)

### レスポンス

#### 成功時 (200)

```json
{
  "coordinates": {
    "latitude": 35.6586,
    "longitude": 139.7454
  },
  "source": "住所: 東京都新宿区",
  "input_type": "address",
  "hazard_info": {
    "jshis_prob_50": {
      "max_prob": 0.85,
      "center_prob": 0.80
    },
    "jshis_prob_60": {
      "max_prob": 0.15,
      "center_prob": 0.12
    },
    "inundation_depth": {
      "max_info": "3m以上5m未満",
      "center_info": "0.5m以上3m未満"
    },
    "tsunami_inundation": {
      "max_info": "浸水想定なし",
      "center_info": "浸水想定なし"
    },
    "hightide_inundation": {
      "max_info": "浸水想定なし",
      "center_info": "浸水想定なし"
    },
    "large_fill_land": {
      "max_info": "あり",
      "center_info": "情報なし"
    },
    "landslide_hazard": {
      "debris_flow": {
        "max_info": "該当なし",
        "center_info": "該当なし"
      },
      "steep_slope": {
        "max_info": "該当なし",
        "center_info": "該当なし"
      },
      "landslide": {
        "max_info": "該当なし",
        "center_info": "該当なし"
      }
    }
  },
  "status": "success"
}
```

#### エラー時

```json
{
  "error": "Invalid coordinates",
  "message": "緯度は24.0〜46.0の範囲で入力してください"
}
```

### レスポンス項目の説明

#### 基本情報
- **coordinates**: 解析された緯度経度
- **source**: 入力元の情報（住所、座標、SUUMO物件など）
- **input_type**: 入力タイプ（"address", "latlon", "suumo_url"）
- **status**: 処理ステータス（"success"）

#### ハザード情報
- **jshis_prob_50/60**: 30年以内の地震発生確率 (震度5強以上/6強以上)
- **inundation_depth**: 想定最大浸水深
- **tsunami_inundation**: 津波浸水想定
- **hightide_inundation**: 高潮浸水想定
- **large_fill_land**: 大規模盛土造成地
- **landslide_hazard**: 土砂災害警戒区域
  - **debris_flow**: 土石流
  - **steep_slope**: 急傾斜地
  - **landslide**: 地すべり

各項目で `max_info` は中心点から半径100m以内の最大値、`center_info` は中心点の値を示します。

#### SUUMO物件の場合
- **property_address**: スクレイピングで取得した物件住所

## デプロイ

1. AWS Lambdaで新しい関数を作成
2. `hazard_api_function.py` をアップロード
3. appフォルダも含めてパッケージング
4. API Gatewayと連携してREST APIを公開

## 使用例

### 住所での検索
```bash
curl "https://api.example.com/hazard-info?input=東京都新宿区"
```

### 緯度経度での検索
```bash
curl "https://api.example.com/hazard-info?input=35.6586,139.7454"
```

### SUUMO URLでの検索
```bash
curl -X POST https://api.example.com/hazard-info \
  -H "Content-Type: application/json" \
  -d '{"input": "https://suumo.jp/chintai/tokyo/example"}'
```

### 従来形式（後方互換性）
```bash
curl "https://api.example.com/hazard-info?lat=35.6586&lon=139.7454"
```

## テスト

```bash
# 関数のテストを実行（24テスト）
python -m pytest tests/test_hazard_api.py -v
```