# テスト環境構築

このプロジェクトにはPytestを使用した自動テストが構築されています。

## テストの実行方法

### 依存関係のインストール
```bash
make install
# または
python3 -m pip install -r requirements.txt
```

### テストの実行
```bash
# 基本的なテスト実行
make test

# カバレッジ付きテスト実行
make test-coverage

# 継続的テスト実行（ファイル変更を監視）
make test-watch
```

## テストファイルの構成

- `tests/test_input_parser.py` - 入力解析のテスト
- `tests/test_geocoding.py` - ジオコーディングのテスト
- `tests/test_line_handler.py` - LINE Botハンドラーのテスト
- `tests/test_lambda_function.py` - Lambdaメイン処理のテスト
- `tests/test_integration.py` - 統合テスト

## テストの特徴

### 使用ライブラリ
- `pytest` - テストフレームワーク
- `pytest-mock` - モック機能
- `pytest-cov` - カバレッジ測定
- `responses` - HTTPリクエストのモック

### テストの種類
1. **単体テスト** - 各モジュールの個別機能をテスト
2. **モックテスト** - 外部APIを含む機能をモック化してテスト
3. **統合テスト** - 全体的なワークフローをテスト

## CI/CDパイプライン

GitHub Actionsを使用してプッシュ時とPR時に自動テストが実行されます。

### 対応Pythonバージョン
- Python 3.9
- Python 3.10
- Python 3.11

## カバレッジレポート

テスト実行後、`htmlcov/index.html`でカバレッジレポートを確認できます。

## テストの追加方法

新しいテストを追加する場合：

1. `tests/` ディレクトリに `test_*.py` ファイルを作成
2. `pytest` の規約に従ってテスト関数を記述
3. モックが必要な場合は `responses` や `pytest-mock` を使用

## トラブルシューティング

### 環境変数が必要なテスト
テストでは環境変数をモック化しています：
```python
with patch.dict('os.environ', {'API_KEY': 'test_key'}):
    # テストコード
```

### 外部APIのテスト
`responses` ライブラリを使用してHTTPリクエストをモック化：
```python
@responses.activate
def test_api_call():
    responses.add(responses.GET, 'https://api.example.com', json={'data': 'test'})
    # テストコード
```