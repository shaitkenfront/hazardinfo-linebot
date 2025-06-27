# LINEチャットボット × AWS Lambda ハザード情報提供アプリ 要件定義書

---

## 🧭 概要

本システムは、LINEチャットボットを通じてユーザーから住所、緯度経度、またはSUUMOの物件URLを受け取り、該当地点の災害リスク情報（ハザード情報）をAWS Lambda上で処理・取得し、LINEメッセージとして返答するサービスである。

---

## 🎯 目的

- 一般ユーザーが身近なLINE上で、災害リスクを手軽に確認できること
- 不動産検討・防災意識向上に役立つ簡易インフラの提供

---

## 👤 ターゲットユーザー

- 引っ越しや購入を検討している不動産関係者・一般市民
- 防災に関心のある地域住民
- 自治体・NPOなど災害リスク情報を扱う機関

---

## 📥 入力仕様

対応するユーザー入力形式：

1. 日本語の住所（例: `東京都世田谷区三軒茶屋1-2-3`）
2. 緯度・経度のカンマ区切り（例: `35.6586, 139.7454`）
3. SUUMOの物件詳細URL（例: `https://suumo.jp/chintai/bc_0000000000/`）

---

## 📤 出力仕様（LINE返信）

ユーザーからの入力に対し、以下の情報を簡潔な自然言語でLINEに返信：

- 今後30年以内に震度5強以上の地震が起こる確率（J-SHIS）
- 今後30年以内に震度6強以上の地震が起こる確率（J-SHIS）
- 想定最大浸水深（国土地理院WMS）
- 土砂災害警戒区域・特別警戒区域の該当有無（WMS）
- 大規模盛土造成地の該当有無（WMS）

---

## 🔧 技術構成

| 項目         | 内容                                  |
|--------------|---------------------------------------|
| フロント     | LINE Messaging API（Webhook連携）     |
| バックエンド | AWS Lambda (Python)                   |
| API Gateway  | Lambda実行のトリガー（Webhook受信）   |
| 外部API      | Google Geocoding API / J-SHIS / 国土地理院WMS |
| スクレイピング | requests + BeautifulSoup によるSUUMO住所抽出（静的HTML想定） |

---

## 🌍 地図情報の取得方法

| 情報種別         | ソース                         | アクセス方法        |
|------------------|----------------------------------|----------------------|
| 地震発生確率     | J-SHIS API (`T30_I50_PS`, `T30_I60_PS`) | GeoJSONデータ取得    |
| 浸水深           | 地理院地図 WMS（浸水想定区域図）    | GetFeatureInfo またはピクセル照会 |
| 土砂災害警戒区域 | 地理院地図 WMS（指定区域レイヤ）     | 同上                 |
| 盛土造成地       | 地理院地図 WMS（大規模盛土マップ）   | 同上                 |

---

## 🚦 入力判定ロジック（Lambda内）

```python
if is_latlon(input_text):
    lat, lon = parse_latlon(input_text)

elif is_suumo_url(input_text):
    address = extract_address_from_suumo(input_text)
    lat, lon = geocode(address)

else:
    lat, lon = geocode(input_text)
