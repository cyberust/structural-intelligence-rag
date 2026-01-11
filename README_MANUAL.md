# AI 戦略プレゼンテーション & チャットボット システム利用マニュアル

**バージョン:** 2.5
**最終更新日:** 2026/01/11

本システムは、お手持ちのドキュメント（PDF, Markdown等）をAIに学習させ、プレゼンテーションと連動して質疑応答を行う **Client-Side RAG（検索拡張生成）システム** です。

利用には **Google Gemini APIキー（無料）** が必須です。

---

## 📂 ディレクトリ構成のルール

本システムは任意の場所で動作しますが、資料とプログラムを分けるため、以下の構成を推奨します。

```text
[任意のプロジェクトフォルダ]
 │
 ├─ chatbot_rag.html         (メインアプリ：ブラウザで開くファイル)
 ├─ requirements.txt         (インストールが必要なライブラリ一覧)
 ├─ rag_index.json           (自動生成される検索用データ)
 │
 ├─ scripts/                 (★重要：Pythonスクリプトはこの中)
 │   └─ build_rag_index.py
 │
 └─ data/                    (★重要：読み込ませたい資料は全てここに入れる)
     ├─ 提案資料.pdf
     ├─ 補足情報.md
     └─ ...

```

---

## 🚀 利用手順（ワークフロー）

以下の **5つのステップ** を順に実行してください。

### Step 1: Gemini APIキーの取得（必須）

本システムはGoogleの生成AIを利用するため、APIキーが必要です。

1. **Google AI Studio** にアクセスします。
* URL: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)


2. Googleアカウントでログインします。
3. **「APIキーを作成 (Create API key)」** ボタンをクリックします。
4. 作成されたキー（`AIza` から始まる文字列）をコピーし、メモ帳などに控えておきます。
* ※このキーは **Step 5** で使用します。



### Step 2: 環境準備（初回のみ）

Pythonライブラリをインストールします。エラーを防ぐため、**管理者権限**で実行してください。

1. Windowsのスタートメニューで「PowerShell」を検索します。
2. **「管理者として実行」** を右クリックまたは選択して起動します。
3. プロジェクトフォルダに移動します。
```powershell
cd [あなたのプロジェクトフォルダのパス]

```


4. ライブラリをインストールします。
```powershell
pip install -r requirements.txt

```



### Step 3: 知識データの作成（重要）

`data` フォルダ内の資料をスキャンし、AIが読める形式（`rag_index.json`）に変換します。
**資料を追加・更新した場合は、必ずこの手順を実行してください。**

PowerShell（管理者）で以下を実行します：
※ `--root data` と指定することで、資料フォルダのみを的確に学習させます。

```powershell
python scripts/build_rag_index.py --root data --out rag_index.json

```

* **オプション（精度向上）:** 取得したAPIキーを使って「意味検索（ベクトル検索）」を行いたい場合：
```powershell
python scripts/build_rag_index.py --root data --out rag_index.json --api-key "あなたのAPIキー"

```



### Step 4: ローカルサーバーの起動

ブラウザのセキュリティ制限（CORSエラー）を回避するため、簡易Webサーバーを立ち上げます。

PowerShell（管理者）で以下を実行します：

```powershell
python -m http.server 8000

```

> **成功確認:** `Serving HTTP on :: port 8000 ...` と表示されればOKです。
> ⚠️ **注意:** このPowerShellウィンドウは **閉じずにそのまま** にしてください（閉じると停止します）。

### Step 5: アプリケーションの開始と認証

1. ブラウザ（Chrome または Edge 推奨）を開きます。
2. アドレスバーに以下のURLを入力してアクセスします。
**[http://localhost:8000/chatbot_rag.html](https://www.google.com/search?q=http://localhost:8000/chatbot_rag.html)**
3. 画面右下の **チャットアイコン（💬）** をクリックします。
4. **「Gemini API Key Required」** という画面が表示されますので、**Step 1** で取得したキーを入力し、「Start Consultation」をクリックしてください。
* これによりAI機能が有効化されます。



---

## ❓ よくある質問とトラブルシューティング

### Q. HTMLファイルをダブルクリックして開いてはいけませんか？

**A. はい、いけません。**
現代のブラウザのセキュリティ仕様により、ローカルファイル（`file://`）からデータファイル（`rag_index.json`）を読み込むことはブロックされます。必ず **Step 4** のサーバー経由（`http://`）でアクセスしてください。

### Q. チャットボットが「参照ファイル」を表示しません。

**A. インデックスが空、または作成されていません。**
**Step 3** のコマンドを実行したか確認してください。また、`data` フォルダの中にファイルが入っているか確認してください。

### Q. PDFファイルが検索にヒットしません。

**A. 画像化されたPDFの可能性があります。**
本ツールはテキストデータを含むPDFのみ対応しています。スキャン画像のみのPDFは、OCRソフト等でテキスト化してから `data` フォルダに配置してください。

---

### 運用コマンド・チートシート

| 目的 | 実行コマンド (管理者権限PowerShell) |
| --- | --- |
| **通常起動**（サーバー立ち上げ） | `python -m http.server 8000` |
| **資料更新**（高速・無料） | `python scripts/build_rag_index.py --root data --out rag_index.json` |
| **資料更新**（高精度・API必須） | `python scripts/build_rag_index.py --root data --out rag_index.json --api-key "KEY"` |
