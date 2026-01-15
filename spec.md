## 1. 技術仕様書 (Specifications)
### A. 動作環境
   OS: Windows 11 (ユーザー環境)

言語: Python 3.10 以上推奨

#### 必須ライブラリ:

- sentence-transformers: ベクトル化（Embedding）担当
- scikit-learn: ベクトル検索（コサイン類似度計算）担当
- google-generativeai: 回答生成（Gemini）担当
- pdfplumber: PDF 解析担当
- torch: 計算バックエンド

###B. ファイル構成
本システムは以下の 3 つのファイルで構成されます。

- build_rag_index_final.py (作成済み)

1. 役割: インデックス構築
2. 入力: 文書フォルダ
3. 出力: rag_index_local.json

- query_rag.py (作成済み・要依存解決)

1. 役割: チャットボット・検索インターフェース
2. 入力: ユーザーの質問、rag_index_local.json、API キー
3. 出力: 回答テキスト

- requirements.txt (要更新)

1. 役割: パッケージ管理定義書

### C. データモデル (JSON 構造)
rag_index_local.json は以下のスキーマを持ちます。

- id: ファイル ID
- source: ファイルパス
- title: タイトル
- text: 本文テキスト
- embedding: 1024 次元のベクトル配列 (List[float])
