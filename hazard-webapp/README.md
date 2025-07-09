# ハザードマップ情報 Webアプリ

住所、緯度経度、SUUMO URLからハザードマップ情報を検索できるNext.js Webアプリケーションです。

## 機能

- **多様な検索方法**
  - 住所による検索（例：東京都新宿区）
  - 緯度経度による検索（例：35.6586, 139.7454）
  - SUUMO URLによる検索
  - 地図クリックによる位置選択

- **ハザード情報表示**
  - 地震発生確率（震度5強以上、6強以上）
  - 浸水リスク（洪水、津波、高潮）
  - 土砂災害リスク（土石流、急傾斜地、地すべり）
  - その他のリスク（大規模盛土造成地）

- **インタラクティブ地図**
  - 国土地理院標準地図
  - クリックによる位置選択
  - 検索結果のマーカー表示

## 技術スタック

- **フロントエンド**: Next.js 14, React 18, TypeScript
- **UI**: Material-UI
- **地図**: Leaflet, React Leaflet
- **状態管理**: React Query
- **HTTP**: Axios
- **バックエンド**: 既存のLambda API

## セットアップ

### 1. 依存関係のインストール

```bash
npm install
```

### 2. 環境変数の設定

`.env.local` ファイルを作成：

```env
HAZARD_API_URL=https://your-api-gateway-url.com
```

### 3. 開発サーバーの起動

```bash
npm run dev
```

ブラウザで http://localhost:3000 を開きます。

## プロジェクト構造

```
src/
├── app/                 # Next.js App Router
│   ├── layout.tsx      # ルートレイアウト
│   ├── page.tsx        # ホームページ
│   └── globals.css     # グローバルスタイル
├── components/         # Reactコンポーネント
│   ├── SearchBar.tsx   # 検索バー
│   ├── HazardMap.tsx   # 地図コンポーネント
│   ├── MapWrapper.tsx  # 地図ラッパー（SSR対応）
│   ├── HazardResultCard.tsx # ハザード情報表示
│   └── ClientProviders.tsx # プロバイダー
├── hooks/              # カスタムフック
│   └── useHazardData.ts # ハザードデータ管理
├── types/              # TypeScript型定義
│   └── hazard.ts       # ハザード関連の型
└── utils/              # ユーティリティ
    ├── api.ts          # API通信
    └── helpers.ts      # ヘルパー関数
```

## API統合

このWebアプリは既存のLambda API（`hazard_api_function.py`）と連携します：

- **エンドポイント**: `/hazard-info`
- **メソッド**: POST（推奨）、GET
- **入力形式**: `{"input": "検索クエリ"}`

## 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# プロダクションビルド
npm run build

# プロダクションサーバー起動
npm run start

# リンター実行
npm run lint

# 型チェック
npm run type-check
```

## デプロイ

### Vercel（推奨）

1. GitHubリポジトリにプッシュ
2. Vercelに接続
3. 環境変数を設定
4. 自動デプロイ

### その他のプラットフォーム

- **Netlify**: `npm run build` → `out/` ディレクトリをデプロイ
- **AWS Amplify**: Git連携で自動デプロイ
- **独自サーバー**: Docker化してデプロイ

## 特徴

- **レスポンシブデザイン**: モバイル・タブレット・デスクトップ対応
- **SSR対応**: SEOフレンドリー
- **TypeScript**: 型安全性
- **パフォーマンス最適化**: React Query によるキャッシュ
- **アクセシビリティ**: Material-UI の標準対応

## ライセンス

MIT