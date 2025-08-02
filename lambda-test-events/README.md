# AWS Lambda テストイベント集

LINE Bot Lambda関数のテスト用JSONイベントファイルです。

## テストファイル一覧

### 基本機能テスト

1. **coordinate-input-test.json**
   - 緯度経度入力テスト（LINE Botメッセージ）
   - 内容: 緯度経度座標 "35.6895, 139.6917"
   - 期待結果: 200 OK、指定座標のハザード情報

2. **address-input-test.json**
   - 住所入力テスト（LINE Botメッセージ）
   - 内容: 住所 "東京都新宿区西新宿2-8-1"
   - 期待結果: 200 OK、住所をジオコーディング後のハザード情報

## テスト実行方法

### AWS Lambda コンソール

1. Lambda関数のページを開く
2. 「テスト」タブを選択
3. 「新しいテストイベントを作成」を選択
4. 上記のJSONファイルの内容をコピー&ペースト
5. テスト名を設定して保存
6. 「テスト」ボタンをクリックして実行

### AWS CLI

```bash
# テストイベントを使用してLambda関数を実行
aws lambda invoke \
  --function-name hazard-api-function \
  --payload file://coordinate-input-test.json \
  --cli-binary-format raw-in-base64-out \
  response.json

# レスポンスを確認
cat response.json
```

## 期待される成功レスポンス例

LINE Botのメッセージに対するレスポンスの場合、ステータスコード200が返されます：

```json
{
  "statusCode": 200,
  "body": ""
}
```

ハザード情報は LINE Messaging API経由でユーザーに返信されます。

## 注意事項

- テスト実行には以下の環境変数の設定が必要です：
  - `HAZARD_MAP_API_URL` - ハザード情報REST API URL
  - `LINE_CHANNEL_ACCESS_TOKEN` - LINE チャンネルアクセストークン
  - `LINE_CHANNEL_SECRET` - LINE チャンネルシークレット
  - `GOOGLE_API_KEY` - Google Geocoding API キー
- 外部ハザード情報REST APIの呼び出しが実際に行われます
- LINE Messaging APIへの返信メッセージ送信が実行されます
- 初回実行時はコールドスタートのため、レスポンスが遅くなる可能性があります

## トラブルシューティング

- **タイムアウト発生**: Lambda関数のタイムアウト設定を30秒以上に設定
- **メモリ不足**: メモリ設定を256MB以上に設定
- **パッケージエラー**: 必要なライブラリ（requests, PIL, shapely等）が含まれているか確認
- **環境変数未設定**: 上記の環境変数が正しく設定されているか確認
- **LINE署名エラー**: テスト時はLINE署名検証を無効化する設定を使用