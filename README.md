# Strategic AI Presentation: Client-Side RAG Architecture

## 概要

本プロジェクトは、サーバーレス環境（ブラウザのみ）で動作する「検索拡張生成（RAG）」搭載のプレゼンテーションシステムです。
単なる静的なスライドではなく、AI エージェントが戦略ドキュメントや競合分析資料を構造的に理解し、プレゼンターのパートナーとして対話に参加します。

## 特徴

- **Client-Side RAG:** Python バックエンドを必要とせず、単一の HTML と JSON インデックスのみで動作。
- **Structural Intelligence:** キーワード検索とベクトル検索（Gemini Embedding）を組み合わせたハイブリッド検索。
- **Privacy First:** API キーはブラウザセッション内でのみ保持され、外部サーバーに保存されません。

## ディレクトリ構成

- `island.io_japan_chatbot_rag.html`: メインアプリケーション（プレゼン＋チャットボット）
- `rag_index.json`: 構造化されたナレッジベース（事前生成済み）
- `scripts/`: インデックス生成用 Python スクリプト

## セットアップ手順（開発者向け）

### 1. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```
