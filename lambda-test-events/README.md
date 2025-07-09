# AWS Lambda テストイベント集

hazard_api_functionのテスト用JSONイベントファイルです。

## テストファイル一覧

### 基本機能テスト

1. **01-basic-coordinate-test.json**
   - 基本的な緯度経度入力テスト
   - 期待結果: 200 OK、東京都庁周辺のハザード情報

2. **02-address-input-test.json**
   - 住所入力テスト
   - 期待結果: 200 OK、新宿区のハザード情報

3. **03-coordinate-string-test.json**
   - 緯度経度文字列入力テスト
   - 期待結果: 200 OK、座標解析後のハザード情報

4. **04-suumo-url-test.json**
   - SUUMO URL入力テスト
   - 期待結果: 200 OK（スクレイピング成功時）、または400（URL無効時）

5. **05-get-coordinate-test.json**
   - GETリクエスト（従来方式）
   - 期待結果: 200 OK、クエリパラメータでの座標指定

6. **06-get-input-test.json**
   - GETリクエスト（柔軟な入力）
   - 期待結果: 200 OK、住所からハザード情報取得

### エラーケーステスト

7. **07-missing-params-test.json**
   - 必須パラメータなし
   - 期待結果: 400 Bad Request、エラーメッセージ

8. **08-invalid-coordinates-test.json**
   - 無効な座標範囲
   - 期待結果: 400 Bad Request、座標範囲エラー

9. **09-invalid-json-test.json**
   - 不正なJSON
   - 期待結果: 400 Bad Request、JSON解析エラー

10. **10-invalid-url-test.json**
    - 無効なURL
    - 期待結果: 400 Bad Request、URL無効エラー

### CORS・その他テスト

11. **11-options-preflight-test.json**
    - OPTIONSリクエスト（プリフライト）
    - 期待結果: 200 OK、CORSヘッダー設定

12. **12-unsupported-method-test.json**
    - サポートされていないHTTPメソッド
    - 期待結果: 405 Method Not Allowed

13. **13-realistic-web-request-test.json**
    - 実際のWebアプリからのリクエスト想定
    - 期待結果: 200 OK、完全なハザード情報

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
  --payload file://01-basic-coordinate-test.json \
  --cli-binary-format raw-in-base64-out \
  response.json

# レスポンスを確認
cat response.json
```

## 期待される成功レスポンス例

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
  },
  "body": "{\"coordinates\":{\"latitude\":35.6586,\"longitude\":139.7454},\"source\":\"座標: 35.6586, 139.7454\",\"input_type\":\"latlon\",\"hazard_info\":{...},\"status\":\"success\"}"
}
```

## 注意事項

- 実際のAPI呼び出しには環境変数の設定が必要です
- SUUMO URLテストは実際のスクレイピングを実行するため、ネットワーク接続が必要です
- 地理院APIやJ-SHIS APIの呼び出しも実際に行われます
- 初回実行時はコールドスタートのため、レスポンスが遅くなる可能性があります

## トラブルシューティング

- **タイムアウト発生**: Lambda関数のタイムアウト設定を30秒以上に設定
- **メモリ不足**: メモリ設定を256MB以上に設定
- **パッケージエラー**: 必要なライブラリ（requests, PIL, shapely等）が含まれているか確認
- **環境変数未設定**: GOOGLE_API_KEYなどの環境変数が設定されているか確認