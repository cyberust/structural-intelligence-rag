# AI 戦略プレゼンテーション & チャットボット 使用マニュアル

**対象者：** 開発経験のないコンサルタント、営業職、経営層

**更新日：** 2026 年 1 月 10 日

**バージョン：** 2.1（ローカルサーバー対応版）

---

## 📋 目次

1. [概要](https://www.google.com/search?q=%23%E6%A6%82%E8%A6%81)
2. [初回セットアップ（5 分）](https://www.google.com/search?q=%23%E5%88%9D%E5%9B%9E%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97)
3. [日常的な使用方法](https://www.google.com/search?q=%23%E6%97%A5%E5%B8%B8%E7%9A%84%E3%81%AA%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95)
4. [ドキュメント追加方法](https://www.google.com/search?q=%23%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88%E8%BF%BD%E5%8A%A0%E6%96%B9%E6%B3%95)
5. [検索方式の選択](https://www.google.com/search?q=%23%E6%A4%9C%E7%B4%A2%E6%96%B9%E5%BC%8F%E3%81%AE%E9%81%B8%E6%8A%9E)
6. [よくある質問](https://www.google.com/search?q=%23%E3%82%88%E3%81%8F%E3%81%82%E3%82%8B%E8%B3%AA%E5%95%8F)
7. [トラブルシューティング](https://www.google.com/search?q=%23%E3%83%88%E3%83%A9%E3%83%96%E3%83%AB%E3%82%B7%E3%83%A5%E3%83%BC%E3%83%86%E3%82%A3%E3%83%B3%E3%82%B0)

---

## 概要

このツールは、**戦略プレゼンテーションと、手元の資料を学習した AI チャットボットを統合したシステム**です。
フォルダ内のドキュメント（PDF, Markdown等）を自動的にインデックス化し、プレゼンターのパートナーとして論理的な回答を提供します。

### 🎯 できること

* ✅ **Client-Side RAG:** サーバーレスで動作し、手元の資料に基づいた正確な回答を生成
* ✅ **ハイブリッド検索:** キーワード検索と意味検索（埋め込み）を併用可能
* ✅ **戦略的プレゼンテーション:** 6 つのスライドによるナラティブの展開
* ✅ **専門家コンサルテーション:** リアルタイムでROI試算や競合比較を実施

### 📦 含まれるもの

| ファイル | 説明 |
| --- | --- |
| `chatbot_rag.html` | **メイン アプリケーション**（プレゼン＋チャット） |
| `rag_index.json` | ナレッジベース（自動生成される検索用辞書） |
| `scripts/build_rag_index.py` | インデックス生成用ツール |
| `requirements.txt` | 必要なライブラリリスト |

---

## 初回セットアップ

### Step 1: Gemini API キーを取得（無料）

1. **Google AI Studio へアクセス**
* ブラウザで [https://aistudio.google.com](https://aistudio.google.com) にアクセスし、Google アカウントでログイン


2. **API キーを生成**
* 「Get API key」または「Create API key」をクリックしてコピー
* **このキーは誰にも教えないでください**



### Step 2: 環境構築（初回のみ）

PowerShell を開き、プロジェクトフォルダ（例: `d:\presentation_rag`）に移動して以下を実行します：

```powershell
cd d:\presentation_rag
pip install -r requirements.txt

```

### Step 3: ローカルサーバーの起動（必須）

セキュリティ（CORS）制限を回避するため、簡易サーバー経由でアクセスします。

1. PowerShell でプロジェクトフォルダにいることを確認し、以下を実行：
```powershell
python -m http.server 8000

```


2. `Serving HTTP on :: port 8000` と表示されたら、**このウィンドウは開いたまま**にしてください（閉じると停止します）。

### Step 4: アプリケーションの起動

1. ブラウザ（Chrome/Edge推奨）で以下のアドレスにアクセス：
**[http://localhost:8000/chatbot_rag.html](https://www.google.com/search?q=http://localhost:8000/chatbot_rag.html)**
2. 右下の 💬 ボタンをクリック
3. Gemini API キーを入力 → 「Start Consultation」をクリック
* ⚠️ **初回のみ必要**（以降はブラウザに記憶されます）



---

## 日常的な使用方法

### 📱 チャットボットで質問する

1. **チャットウィンドウを開く**
* 右下の 💬 ボタンをクリック


2. **質問を入力**
* 例：「VDI 比でコスト削減効果はどのくらい？」「競合製品との違いは？」


3. **回答を確認**
* 回答の末尾（または直前）に、根拠となった**参照ファイル名**が表示されます。
* 表示例：`【参照ファイル】・ROI分析レポート.md ・競合比較表.pdf`



### 📊 スライド操作

* **← / → キー** または画面左下の矢印ボタンでスライドを遷移します。

---

## ドキュメント追加方法

新しい資料（PDFやMarkdown）を知識ベースに追加する手順です。

### 1. ドキュメントを配置

プロジェクトフォルダ内にファイルをコピーします。サブフォルダ（例: `data/`）に入れても認識されます。

### 2. インデックスの更新（ビルド）

PowerShell で以下を実行し、`rag_index.json` を更新します。

**A. キーワード検索モード（高速・無料）**

```powershell
python scripts/build_rag_index.py --root . --out rag_index.json

```

**B. 意味検索モード（高精度・推奨）**
※ APIキーを使って、テキストの意味（ベクトル）を埋め込みます。

```powershell
python scripts/build_rag_index.py --root . --out rag_index.json --api-key "あなたのAPIキー"

```

### 3. 反映

ブラウザをリロード（F5）すると、新しい知識が反映されます。

---

## トラブルシューティング

### 🔴 問題: 「チャットが応答しない / ファイル名が表示されない」

**原因：** `file://` で開いているため、セキュリティ機能によりファイルの読み込みがブロックされています。
**解決策：** 必ず **Step 3** の手順に従い、`http://localhost:8000/...` でアクセスしてください。

### 🔴 問題: 「"RAG index fetch error" と表示される」

**原因：** `rag_index.json` が見つからないか、サーバーが起動していません。
**解決策：**

1. `python scripts/build_rag_index.py ...` を実行して json を生成済みか確認。
2. PowerShell で `python -m http.server 8000` が動いているか確認。

### 🔴 問題: 「特定のPDFが検索されない」

**原因：** PDFが「画像化」されていてテキストデータを含んでいない可能性があります。
**解決策：** PDFを開き、マウスで文字を選択できるか確認してください。選択できない場合、OCRソフト等でテキスト化する必要があります。

---

## 🎓 ファイル構成

```
d:\presentation_rag\
│
├─ chatbot_rag.html         ← ブラウザで開くファイル
├─ rag_index.json           ← 知識データベース（自動更新）
├─ requirements.txt         ← 設定ファイル
│
├─ scripts/
│  └─ build_rag_index.py    ← インデックス生成ツール
│
├─ README_MANUAL.md         ← このマニュアル
│
└─ data/                    ← 読み込ませたい資料置き場
   ├─ 提案資料.pdf
   ├─ 補足情報.md
   └─ ...

```

---

## 📞 サポート情報

不具合報告時には、ブラウザの「開発者ツール（F12）」→「Console」タブに表示されている**赤字のエラーメッセージ**をご確認ください。

**推奨環境:** Windows 10/11, macOS, Linux + Google Chrome / Microsoft Edge
