import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import ClientProviders from '@/components/ClientProviders';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'ハザードマップ情報 - 災害リスク検索',
  description: '住所や緯度経度からハザードマップ情報を検索できるWebアプリケーションです',
  keywords: ['ハザードマップ', '災害', '地震', '浸水', '土砂災害', 'リスク評価'],
  authors: [{ name: 'Hazard Info Team' }],
  openGraph: {
    title: 'ハザードマップ情報',
    description: '住所や緯度経度からハザードマップ情報を検索',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
          integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
          crossOrigin=""
        />
      </head>
      <body className={inter.className}>
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}