# index.html 分析レポートと改善提案

## 現状分析 (Current State Analysis)

ユーザーから提示された「目的とゴール」に対し、現在の [index.html](file:///d:/island/RAG/index.html) の実装には重大なギャップが存在します。

### 1. 検索ロジックの乖離 (Critical Gap)
*   **要件**: 「ローカル完結型のセマンティック検索（RAG）」
*   **現状**: [index.html](file:///d:/island/RAG/index.html) (327-364行目) の `scoreByKeywords` 関数は、単なる**キーワード一致（`includes`）**を行っているだけです。
    *   ベクトル検索（意味検索）が行われていないため、「GDPR」という単語が含まれていないが「個人情報保護」について書かれているドキュメントはヒットしません。
    *   併記されている [query_rag.py](file:///d:/island/RAG/query_rag.py) には `SentenceTransformer` (E5モデル) とコサイン類似度を使った正しい実装がありますが、これがプレゼンテーション画面 ([index.html](file:///d:/island/RAG/index.html)) からは利用されていません。

### 2. データ活用と更新フロー
*   **要件**: CI/CD統合、自動更新。
*   **現状**: [rag_index.json](file:///d:/island/RAG/rag_index.json) を `fetch` する仕組みは整っており、アーキテクチャとしては優秀です。ただし、このJSONに含まれるデータ構造（Embeddingが含まれているか等）と、フロントエンド側の検索ロジックが噛み合っていません（現在はテキストのみを使用）。

### 3. コンテキスト認識の不足
*   **要件**: 「その場で最適解を提示」。
*   **現状**: チャットボットは「プレゼンテーションの現在地（どのスライドを開いているか）」を知りません。聴衆から「このスライドのこの数字はどういう根拠？」と聞かれた際、ボットはスライドの内容を参照できません。

---

## 改善提案 (Improvement Proposal)

「ローカル完結」「ブラウザだけで動作（Presentation as Code）」という利点を損なわず、真のセマンティックRAGを実現するための提案です。

### アプローチ: ブラウザ完結型ハイブリッド検索 (Browser-Native RAG)

Pythonバックエンドサーバーを立てずに、**Webブラウザ(JavaScript)だけでベクトル検索を完結させる**構成を提案します。

#### 1. 検索エンジンの刷新 (Keyword → Vector)
`transformers.js` を導入、または [rag_index.json](file:///d:/island/RAG/rag_index.json) にPython側で事前に計算したベクトルを埋め込み、JS側で「コサイン類似度計算」を行います。
*   **Before**: キーワードが含まれるかどうかで判定
*   **After**: ユーザーの質問ベクトルと、ドキュメントベクトルの類似度（距離）で判定。

> **推奨プラン**:
> ブラウザでのEmbedding計算は重いため、**「Python([build_rag_index.py](file:///d:/island/RAG/build_rag_index.py))で事前にベクトル化 → JSONに保存 → JSはコサイン類似度計算のみ実行」**という方式が最も軽量で高速です。

#### 2. スライドコンテキストの注入
現在表示中のスライド（コンポーネント）のテキスト情報を、システムプロンプトに動的に注入します。
*   **効果**: 「このページのROIの根拠は？」という指示語を含む質問に回答可能になります。

#### 3. UI/UXの強化
*   **Markdown表示**: 回答テキストを `react-markdown` でレンダリングし、表組みや箇条書きを綺麗に表示します。
*   **ストリーミング表示**: Gemini APIのレスポンスをタイプライター風にストリーミング表示し、待機時間の体感を短縮します。

---

## Technical Implementation Steps

この提案を採用する場合、以下の手順で実装を行います。

1.  **[build_rag_index.py](file:///d:/island/RAG/build_rag_index.py) の改修**:
    *   Gemini Embedding API ではなく、ローカルLLM (SentenceTransformer/E5) を使用してベクトルを生成・保存するように変更（[query_rag.py](file:///d:/island/RAG/query_rag.py) と統一）。
    *   APIキー不要でビルド可能にします。

2.  **[index.html](file:///d:/island/RAG/index.html) のアルゴリズム置換**:
    *   `scoreByKeywords` を廃止し、`cosineSimilarity` 関数を実装。
    *   質問文のベクトル化には、軽量な `transformers.js` または Gemini Embedding API (要APIキー) を利用。
    *   ※ユーザー体験（速度）を優先するなら、質問文のベクトル化だけ API (Gemini) に頼るのが最も現実的で高速です（ドキュメントベクトルはローカルにあるため、検索自体はブラウザ内で完結）。

3.  **UIコンポーネント追加**:
    *   `react-markdown`, `remark-gfm` のCDN追加。
    *   チャットコンポーネントの改修。

この改善案について、承認または調整の指示をお願いします。
