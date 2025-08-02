# hazardinfo-linebot

ハザードマップ情報を取得して回答するLINEチャットボット

## 概要

このプロジェクトは、LINEチャットボットを通じてユーザーから住所や緯度経度を受け取り、該当地点の災害リスク情報（ハザード情報）を外部REST APIから取得し、LINEメッセージとして返答するサービスです。

## 機能

- **LINE Bot機能**: LINEを通じてハザード情報を提供
- **多様な入力形式対応**:
  - 日本語住所（例: `東京都世田谷区三軒茶屋1-2-3`）
  - 緯度・経度（例: `35.6586, 139.7454`）
- **包括的ハザード情報**:
  - 地震発生確率（震度5強以上、震度6強以上）
  - 想定最大浸水深（洪水、津波、高潮）
  - 土砂災害警戒区域（土石流、急傾斜地、地すべり）
  - 大規模盛土造成地情報

## 技術構成

| 項目 | 内容 |
|------|------|
| フロントエンド | LINE Messaging API（Webhook連携） |
| バックエンド | AWS Lambda (Python) |
| API Gateway | Lambda実行のトリガー（Webhook受信） |
| 外部API | 外部ハザード情報REST API、Google Geocoding API |

## アーキテクチャ

```
LINE Bot → API Gateway → AWS Lambda → 外部ハザード情報REST API
                               ↓
                        Google Geocoding API (住所→座標変換)
```

### 主要モジュール

- `lambda_function.py` - AWS Lambdaエントリポイント
- `app/hazard_api_client.py` - 外部ハザード情報REST APIクライアント
- `app/display_formatter.py` - ハザード情報の表示フォーマット
- `app/input_parser.py` - 入力形式の判定
- `app/geocoding.py` - 住所から座標への変換
- `app/line_handler.py` - LINE Messaging API連携

## セットアップ

### 1. 環境変数の設定

以下の環境変数を設定する必要があります：

```bash
# 必須
HAZARD_MAP_API_URL=https://your-hazard-api-endpoint.com
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# オプション（住所入力時のフォールバック用）
GOOGLE_API_KEY=your_google_api_key

# テスト用（デフォルト: test_signature）
LINE_TEST_SIGNATURE=test_signature
```

### 2. 依存関係のインストール

```bash
# 仮想環境の作成と有効化
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. AWS Lambda デプロイ

このプロジェクトはAWS Lambda関数として動作するように設計されています。`lambda_function.py`がエントリポイントです。

### 4. LINE Developers設定

1. LINE Developers コンソールでチャネルを作成
2. Webhook URLをAWS LambdaのAPI Gateway URLに設定
3. チャネルアクセストークンとチャネルシークレットを環境変数に設定

## 使用方法

### LINE Botでの使用

LINEで以下のような入力が可能です：

- `東京都千代田区` (住所)
- `35.6895,139.6917` (緯度経度)

ボットが該当地点のハザード情報を返信します。

## テスト

### 単体テスト

```bash
# テストの実行
pytest

# 特定のテストファイルのみ
pytest tests/test_lambda_function.py -v
```

### Lambda関数のテスト

本プロジェクトにはテスト用のLambdaイベントファイルが含まれており、LINE APIを実際に呼び出すことなくテストできます。

#### テスト用環境変数設定

```bash
# テスト用署名（この署名を使用するとLINE APIへの実際の送信をスキップ）
LINE_TEST_SIGNATURE=test_signature
```

#### 利用可能なテストファイル

- `lambda-test-events/address-input-test.json` - 住所入力テスト
- `lambda-test-events/coordinate-input-test.json` - 緯度経度入力テスト  

#### AWS CLIでのテスト実行

```bash
# 住所入力テスト
aws lambda invoke \
  --function-name your-function-name \
  --payload file://lambda-test-events/address-input-test.json \
  --cli-binary-format raw-in-base64-out \
  response.json

# レスポンス確認
cat response.json
```

#### テスト時のレスポンス例

テスト署名を使用した場合、LINE APIは呼び出されず、Lambda応答に詳細な処理結果が含まれます：

```json
{
  "statusCode": 200,
  "body": {
    "status": "OK",
    "test_mode": true,
    "line_processing_result": {
      "test_mode": true,
      "processed_events": 1,
      "line_responses": [
        {
          "user_message": "東京都新宿区西新宿2-8-1",
          "bot_response": "「東京都新宿区西新宿2-8-1」周辺のハザード情報です。\n【30年以内に震度5強以上の地震が起こる確率】\n...",
          "line_result": {
            "test_mode": true,
            "line_payload": {
              "replyToken": "test_reply_token_12345",
              "messages": [{"type": "text", "text": "..."}]
            }
          }
        }
      ]
    }
  }
}
```

#### AWS Lambdaコンソールでのテスト

1. Lambda関数のページを開く
2. 「テスト」タブを選択
3. 「新しいテストイベントを作成」を選択
4. 上記のJSONファイルの内容をコピー&ペースト
5. テスト名を設定して保存
6. 「テスト」ボタンをクリックして実行

テスト署名により、実際のLINE送信は行われず、レスポンスでボットの返答内容を確認できます。

## 外部依存関係

- **外部ハザード情報REST API**: `HAZARD_MAP_API_URL`で指定されるAPI（リポジトリ: https://github.com/shaitkenfront/hazardinfo-restapi）
- **Google Geocoding API**: 住所から座標への変換（オプション）
- **LINE Messaging API**: チャットボット機能

## ライセンス

MIT License
