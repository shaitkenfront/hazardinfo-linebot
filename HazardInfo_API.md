# Hazard Info REST API 仕様書

## 1. 概要

このAPIは、日本の任意の地点におけるハザード情報を提供します。住所や緯度経度を指定することで、地震発生確率、浸水深、土砂災害警戒区域、大規模盛土造成地などの情報を取得できます。

## 2. エンドポイント

AWS Lambda関数としてデプロイされることを想定しています。

- **本番環境:** `(設定されたAPI GatewayのURL)`
- **ステージング環境:** `(設定されたAPI GatewayのURL)`

## 3. 認証

APIの利用には、APIキーが必要です。リクエストヘッダーに `x-api-key` としてAPIキーを含めてください。

```
x-api-key: YOUR_API_KEY
```

## 4. リクエスト

### 4.1. HTTPメソッド

`GET` と `POST` の両方のメソッドをサポートしています。

### 4.2. パラメータ

#### 4.2.1. 必須パラメータ

以下のいずれかのパラメータが必須です。

| パラメータ名 | 型 | 説明 |
| :--- | :--- | :--- |
| `lat`, `lon` | `number` | 緯度と経度を指定します。 |
| `input` | `string` | 住所や場所の名前を指定します。内部でジオコーディングされ、緯度経度に変換されます。 |

#### 4.2.2. オプションパラメータ

| パラメータ名 | 型 | 説明 | デフォルト値 |
| :--- | :--- | :--- | :--- |
| `datum` | `string` | 入力座標の測地系を指定します。`wgs84` (世界測地系) または `tokyo` (日本測地系) を選択できます。 | `wgs84` |
| `hazard_types` | `string` or `array` | 取得したいハザード情報の種類をカンマ区切りの文字列または配列で指定します。指定しない場合は、すべてのハザード情報を取得します。 | `null` (すべて) |
| `search_points` | `number` | 検索精度を指定します。`4` (高速モード) または `8` (高精度モード) を選択できます。 | `4` |

#### 4.2.3. 利用可能なハザードタイプ (`hazard_types`)

| 値 | 説明 |
| :--- | :--- |
| `earthquake` | 30年以内の震度5強以上および6強以上の地震発生確率 |
| `flood` | 想定最大浸水深 |
| `tsunami` | 津波による想定浸水深 |
| `high_tide` | 高潮による想定浸水深 |
| `landslide` | 土砂災害警戒区域（土石流、急傾斜地、地すべり） |
| `large_fill_land` | 大規模盛土造成地 |

### 4.3. リクエスト例

#### GETリクエスト

- **緯度経度で指定**
  ```
  /prod/hazardinfo?lat=35.681236&lon=139.767125
  ```
- **住所で指定し、特定のハザード情報（地震と洪水）を取得**
  ```
  /prod/hazardinfo?input=東京都千代田区丸の内１丁目&hazard_types=earthquake,flood
  ```

#### POSTリクエスト

- **リクエストボディ**
  ```json
  {
    "lat": 35.681236,
    "lon": 139.767125,
    "datum": "wgs84",
    "hazard_types": ["tsunami", "landslide"],
    "search_points": 8
  }
  ```

## 5. レスポンス

### 5.1. 成功時のレスポンス (`200 OK`)

```json
{
  "coordinates": {
    "latitude": 35.681236,
    "longitude": 139.767125
  },
  "source": "住所: 東京都千代田区丸の内１丁目",
  "input_type": "address",
  "requested_hazard_types": ["earthquake", "flood"],
  "hazard_info": {
    "jshis_prob_50": {
      "max_prob": "3%",
      "center_prob": "3%"
    },
    "jshis_prob_60": {
      "max_prob": "1%",
      "center_prob": "1%"
    },
    "inundation_depth": {
      "max_info": "0.5m未満",
      "center_info": "浸水なし"
    },
    "large_fill_land": {
      "max_info": "あり",
      "center_info": "あり"
    }
  },
  "status": "success"
}
```

### 5.2. レスポンスフィールドの説明

| フィールド名 | 型 | 説明 |
| :--- | :--- | :--- |
| `coordinates` | `object` | 緯度経度の情報 |
| `coordinates.latitude` | `number` | 緯度 |
| `coordinates.longitude` | `number` | 経度 |
| `source` | `string` | 入力情報のソース（住所または座標） |
| `input_type` | `string` | 入力情報の種類 (`address` または `latlon`) |
| `requested_hazard_types` | `array` | リクエストされたハザード情報のリスト |
| `hazard_info` | `object` | ハザード情報の詳細 |
| `status` | `string` | 処理のステータス |

### 5.3. エラーレスポンス

#### 400 Bad Request (パラメータが不正)

```json
{
  "error": "Invalid hazard_types parameter",
  "message": "Invalid hazard types: ['invalid_type']",
  "valid_types": ["earthquake", "flood", "tsunami", "high_tide", "landslide", "large_fill_land"]
}
```

#### 404 Not Found (場所が見つからない)

```json
{
  "error": "Location not found",
  "message": "場所を特定できませんでした。住所やURLを確認してください。"
}
```

#### 500 Internal Server Error (サーバー内部エラー)

```json
{
  "error": "Internal server error",
  "message": "An error occurred while processing the request: (エラー詳細)"
}
```

## 6. 注意事項

- **大規模盛土造成地情報について:** この情報は、`hazard_types` パラメータに `large_fill_land` を含まれている場合にのみ提供されます。
- **パフォーマンス:** `search_points` パラメータを `8` (高精度モード) に設定すると、レスポンスタイムが長くなる可能性があります。
- **データソース:** 本APIが提供する情報は、国土地理院やJ-SHISなどの公的機関のデータを基にしていますが、情報の正確性や完全性を保証するものではありません。最終的な判断は、公的機関が発表する一次情報をご確認ください。
