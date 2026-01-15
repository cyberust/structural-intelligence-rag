# Strategic AI Presentation: Hybrid RAG Architecture

## 概要
本プロジェクトは、ローカル環境での高度な「意味検索（Semantic Search）」と、クラウドAIによる「回答生成」を組み合わせたハイブリッド型RAGシステムです。
Pythonによるローカル処理でドキュメントをインデックス化し、Webブラウザ上のインターフェースでAIと対話しながらプレゼンテーションを行います。

## 特徴
* **Local & Secure:** 検索（Embedding）はローカルPCで完結。プライバシーを確保。
* **Hybrid Intelligence:** 高精度なE5モデル（ローカル）とGemini（クラウド）のハイブリッド構成。
* **Interactive Presentation:** プレゼン中にリアルタイムで資料に基づく回答を生成。

## クイックスタート
1. **準備**: `pip install -r requirements.txt`
2. **構築**: `python build_rag_index.py --root data --out rag_index_local.json`
3. **起動**: `start_presentation.bat` をダブルクリック

詳細は [README_MANUAL.md](./README_MANUAL.md) を参照してください。

## ライセンス
MIT License / Copyright (c) 2026 Yasuyuki Sakane
