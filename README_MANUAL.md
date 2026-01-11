# AI 戦略プレゼンテーション & チャットボット システム利用マニュアル

**バージョン:** 2.6
**最終更新日:** 2026/01/11

本システムは、お手持ちのドキュメント（PDF, Markdown等）をAIに学習させ、プレゼンテーションと連動して質疑応答を行う **Client-Side RAG（検索拡張生成）システム** です。

利用には **Google Gemini APIキー（無料）** が必須です。

---

## 📂 ディレクトリ構成のルール

本システムは任意の場所で動作しますが、資料とプログラムを分けるため、以下の構成を推奨します。

```text
[任意のプロジェクトフォルダ]
 │
 ├─ start_presentation.bat   (★重要：起動用ショートカット)
 ├─ chatbot_rag.html         (メインアプリ)
 ├─ requirements.txt         (設定ファイル)
 ├─ rag_index.json           (自動生成される検索用データ)
 │
 ├─ scripts/                 (インデックス生成スクリプト)
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

```powershell
python scripts/build_rag_index.py --root data --out rag_index.json

```

* **オプション（精度向上）:** 取得したAPIキーを使って「意味検索（ベクトル検索）」を行いたい場合：
```powershell
python scripts/build_rag_index.py --root data --out rag_index.json --api-key "あなたのAPIキー"

```



### Step 4: アプリケーションの起動

フォルダ内にある **`start_presentation.bat`** をダブルクリックします。

* 自動的に「黒い画面（サーバー）」が立ち上がり、続いて「ブラウザ」が開いてシステムが表示されます。
* ⚠️ **注意:** 黒い画面はシステムの裏側で動いているサーバーですので、**閉じずにそのまま** にしてください（閉じると停止します）。

### Step 5: コンサルテーションの開始

1. ブラウザ画面右下の **チャットアイコン（💬）** をクリックします。
2. **「Gemini API Key Required」** という画面が表示されます。
3. **Step 1** で取得したキーを入力し、「Start Consultation」をクリックしてください。
* これによりAI機能が有効化されます。



---

## ❓ よくある質問とトラブルシューティング

### Q. HTMLファイルを直接ダブルクリックしてはいけませんか？

**A. はい、いけません。**
セキュリティ制限により、直接開くと資料データが読み込めません。必ず **`start_presentation.bat`** から起動するか、サーバー経由（`http://localhost:8000`）でアクセスしてください。

### Q. チャットボットが「参照ファイル」を表示しません。

**A. インデックスが空、または作成されていません。**
**Step 3** のコマンドを実行したか確認してください。また、`data` フォルダの中にファイルが入っているか確認してください。

### Q. PDFファイルが検索にヒットしません。

**A. 画像化されたPDFの可能性があります。**
本ツールはテキストデータを含むPDFのみ対応しています。スキャン画像のみのPDFは、OCRソフト等でテキスト化してから `data` フォルダに配置してください。

---

### 運用コマンド・チートシート

| 目的 | 方法 |
| --- | --- |
| **システムの起動** | `start_presentation.bat` をダブルクリック |
| **資料更新**（高速・無料） | `python scripts/build_rag_index.py --root data --out rag_index.json` |
| **資料更新**（高精度・API必須） | `python scripts/build_rag_index.py --root data --out rag_index.json --api-key "KEY"` |

```

```
