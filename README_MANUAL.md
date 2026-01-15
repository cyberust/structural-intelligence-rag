# AI戦略プレゼンテーション & チャットボット システム利用マニュアル

バージョン: 3.3 (Hybrid RAG Edition)  
最終更新日: 2026/01/15  

本システムは、お手持ちのドキュメント（PDF, Markdown, HTML等）をローカル環境で学習（ベクトル化）し、  
Google Gemini AIを用いて高精度な質疑応答とプレゼンテーションを実現する **Hybrid RAG（検索拡張生成）システム** です。  

利用には **Google Gemini APIキー（無料枠あり）** が必須です。  

---

## 1. 動作環境（Prerequisites）

| 項目 | 要件 |
| --- | --- |
| OS | Windows 10/11, macOS, Linux |
| Python | 3.10 以上（必須） |
| RAM | 8GB以上（ローカルAIモデル展開のため推奨） |
| インターネット | 必須（Gemini APIアクセスのため） |

---

## 2. ディレクトリ構成

```text
.
├── start_presentation.bat     # プレゼンテーション起動スクリプト（ブラウザUI）
├── index.html                 # Webプレゼン＆チャットUI
├── query_rag.py               # CUIチャットボット（検証用）
├── build_rag_index.py         # 知識データ（インデックス）生成ツール
├── rag_index_local.json       # ベクトル化された知識データ
├── requirements.txt           # 必要ライブラリ一覧
├── README_MANUAL.md           # 本マニュアル
│
└── data/                      # ドキュメント置き場
    ├── 提案資料.pdf
    └── ...
````

---

## 3. 利用手順（セットアップ〜実行）

### Step 1. Gemini APIキーの取得（必須）

1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン
3. 「Create API key（APIキーを作成）」をクリック
4. 表示されたキー（`AIza` で始まる文字列）をコピーし、安全に保管

このキーは後述のチャット／プレゼン起動時に使用します。

---

### Step 2. 環境構築（初回のみ）

1. **PowerShell** または **Terminal** を開き、プロジェクトフォルダに移動

```powershell
cd [あなたのプロジェクトフォルダのパス]
```

2. **依存ライブラリを一括インストール**

```powershell
pip install -r requirements.txt
```

※ 数分かかる場合があります。エラーが出た場合は Python のバージョンを確認してください。

---

### Step 3. 知識データの生成（ローカルIndex作成）

`data` フォルダ内の資料をAIが読み取り、検索可能なベクトル形式に変換します。

```powershell
python build_rag_index.py --root data --out rag_index_local.json
```

* **初回実行時:** 約2GBのAIモデルを自動ダウンロード（時間がかかります）
* **2回目以降:** 追加・変更分のみを高速処理（レジューム対応）

---

### Step 4. プレゼンテーションの起動（Web UI）

グラフィカルなプレゼン＆チャット環境を起動します。

1. フォルダ内の **start_presentation.bat** をダブルクリック
2. 黒い画面（ローカルサーバー）が開き、ブラウザが自動起動
3. 画面上で **APIキー** を入力し、「Start」をクリック

以後、プレゼン中にチャット欄からAIに質問・要約・説明を行うことが可能です。

---

### Step 5. CUIモードでの確認（任意）

GUIを使わずに動作確認・テキストテストを行いたい場合：

```powershell
python query_rag.py --api-key "あなたのAPIキー"
```

* 対話プロンプトが起動します。
* 質問を入力すると、ローカル検索＋Gemini生成による回答が表示されます。

---

## 4. トラブルシューティング（FAQ）

### Q1. インデックス作成中に "MemoryError" や停止が発生する

A. メモリ不足です。`build_rag_index.py` 内の `BATCH_SIZE` を
`8` → `4` または `1` に変更し再実行してください。

---

### Q2. PDFが読み込まれない

A. 画像PDFまたは暗号化PDFの可能性があります。
スキャンPDFはOCRでテキスト化後、`data` に配置してください。

---

### Q3. 「資料には情報がありません」と出る

A. 検索キーワードが短すぎる／インデックス破損の可能性があります。

* より具体的な質問にする（例：「この資料の提案内容を要約して」）
* `rag_index_local.json` を削除後、Step 3を再実行してください。

---

### Q4. ブラウザで "404 Not Found" になる

A. `start_presentation.bat` 内の `index.html` のファイル名を確認し、一致させてください。

---

## 5. 運用チートシート

| 操作          | コマンド／手順                                                            |
| ----------- | ------------------------------------------------------------------ |
| 依存関係インストール  | `pip install -r requirements.txt`                                  |
| 知識データ作成     | `python build_rag_index.py --root data --out rag_index_local.json` |
| チャット起動（CUI） | `python query_rag.py --api-key "KEY"`                              |
| プレゼン起動（Web） | `start_presentation.bat` を実行                                       |
| 強制再構築       | `rag_index_local.json` を削除後、Step 3 再実行                             |

---

## 6. 補足：関連ファイル

### start_presentation.bat

```batch
@echo off
cd /d %~dp0
echo ========================================================
echo  AI プレゼンテーションシステムを起動しています...
echo  この黒い画面は閉じないでください（閉じるとサーバー停止）。
echo ========================================================

:: ブラウザを自動起動
start http://localhost:8000/index.html

:: ローカルサーバー起動
python -m http.server 8000
```

---

## 7. 技術仕様概要

```markdown
# 技術仕様書 (Technical Specification)

## 構成概要
- 検索（R）: ローカルで文書をベクトル化（E5モデル）
- 生成（G）: Gemini APIで回答生成
- 結果: 検索強化型生成 (Hybrid RAG)

## 処理フロー
1. build_rag_index.py  
   → 文書解析 → ベクトル生成 → rag_index_local.json  
2. query_rag.py  
   → 質問ベクトル化 → コサイン類似検索 → Geminiへ送信  
3. index.html  
   → JSからローカルデータ検索 + Gemini連携  

## 依存ライブラリ
- sentence-transformers  
- google-generativeai  
- scikit-learn  
- pdfplumber  
- html.parser  

## 制約
- Batch Size: デフォルト8（調整可）  
- Max Length: 各ドキュメント8,000文字  
- Prefixルール: 登録時`passage:` / 検索時`query:` を付与
```

## 8. 補足：query_rag.py の役割と利用方針

本プロジェクトには、ブラウザ完結型（Client-Side RAG） と Python検証ツール（CUI版） の2つの利用形態があります。

### 1. query_rag.py の目的

このファイルは、AI検索および回答生成の動作を検証するための開発・テスト用ツールです。ブラウザ版（index.html）とは異なり、ローカルのPython環境のみで動作します。

### 2. ユーザ環境での必要性

目的が「プレゼンテーション（ブラウザUI）の完成と運用」である場合、
query_rag.pyは必要ありません。

### 3. 必須構成：

| 種別 | ファイル                     | 用途                 |
| -- | ------------------------ | ------------------ |
| 必須 | `build_rag_index.py`     | 資料のベクトル化（知識データ生成）  |
| 必須 | `index.html`             | プレゼン＆チャット画面        |
| 必須 | `start_presentation.bat` | ローカルWebサーバー起動      |
| 任意 | `query_rag.py`           | 開発・動作検証用（通常運用では不要） |

---
