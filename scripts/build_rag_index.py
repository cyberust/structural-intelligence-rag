#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGインデックス構築スクリプト (Lint修正済み)
- モデル: intfloat/multilingual-e5-large (高精度・日本語対応)
- 機能: HTML/Markdownクリーニング、バッチ処理、差分更新(レジューム)
- 完全オフライン動作
"""

import os
import sys
import json
import argparse
import warnings
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from html.parser import HTMLParser

# === 依存ライブラリ ===
try:
    import pdfplumber  # type: ignore
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: pdfplumber not installed. PDF support disabled.")

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    LOCAL_EMBEDDING_SUPPORT = True
except ImportError:
    LOCAL_EMBEDDING_SUPPORT = False
    print("Error: sentence-transformers not installed.")
    print("Run: pip install sentence-transformers torch")
    sys.exit(1)

# ログ抑制
import logging
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)


# === 設定 ===
class Config:
    """設定クラス"""
    # 高精度モデル (E5-large)
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-large"

    # E5モデルは "passage: " というプレフィックスが必要
    PREFIX: str = "passage: "

    # テキスト処理
    MAX_TEXT_LENGTH: int = 8000

    # バッチ処理 (VRAM不足なら小さくする: 4 or 8)
    BATCH_SIZE: int = 8

    # 保存間隔 (バッチ数ごと)
    SAVE_INTERVAL: int = 10

    SUPPRESS_PDF_WARNINGS: bool = True


# === HTML処理クラス ===
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._texts = []
        self._skip = False
        self._skip_tags = {"script", "style", "noscript", "meta"}

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False

    def handle_data(self, data):
        if not self._skip and data and data.strip():
            self._texts.append(data.strip())

    def get_text(self):
        return " ".join(self._texts)


# === ユーティリティ ===
def sanitize_filename(filename: str) -> str:
    s = re.sub(r'[^\w\s\-\.]', '_', filename).lower()
    return s.replace(' ', '_')


def extract_text_from_file(path: Path) -> tuple[Optional[str], str]:
    """
    ファイルパスから (タイトル, テキスト) を抽出
    拡張子に応じてHTML処理やPDF処理を分岐
    """
    ext = path.suffix.lower()
    title = path.stem
    text = ""

    try:
        if ext == '.pdf':
            if not PDF_SUPPORT:
                return None, ""
            # PDF処理
            pages = []
            if Config.SUPPRESS_PDF_WARNINGS:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    with pdfplumber.open(path) as pdf:
                        for page in pdf.pages:
                            t = page.extract_text()
                            if t:
                                pages.append(t)
            else:
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            pages.append(t)

            if not pages:
                return None, ""
            text = "\n".join(pages)

        elif ext in {'.html', '.htm'}:
            # HTML処理 (タグ除去)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()

            # タイトル抽出
            m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
            if m:
                title = re.sub(r"\s+", " ", m.group(1)).strip()

            # 本文抽出
            parser = HTMLTextExtractor()
            parser.feed(raw)
            text = parser.get_text()

        else:
            # Markdown/Text処理
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()

            # Markdownタイトル抽出 (# 見出し)
            for line in raw.splitlines():
                if line.startswith("# "):
                    title = line.strip("# ").strip()
                    break
            text = raw

    except Exception as e:
        print(f"Warning: Failed to read {path.name}: {e}")
        return None, ""

    # 共通クリーニング
    text = re.sub(r'\s+', ' ', text).strip()
    return title, text


# === Embedding生成クラス ===
class LocalEmbeddingGenerator:
    def __init__(self, model_name: str = Config.EMBEDDING_MODEL):
        print(f"\nLoading model: {model_name} ...")
        print("(This may take time on first run)")
        self.model = SentenceTransformer(model_name)
        print("✓ Model loaded\n")

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        # E5モデル用にプレフィックス "passage: " を付与
        inputs = [Config.PREFIX + t for t in texts]

        embeddings = self.model.encode(
            inputs,
            batch_size=Config.BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings.tolist()


# === インデックス構築 ===
def build_index(root_dir: str, output_path: str, use_batch: bool = True):
    root_path = Path(root_dir).resolve()
    print(f"Target: {root_path}")
    print(f"Output: {output_path}")

    # 1. レジューム機能: 既存データの読み込み
    existing_docs: Dict[str, Any] = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ソースパスをキーにして高速検索可能に
                existing_docs = {item['source']: item for item in data}
            print(f"Resume: Loaded {len(existing_docs)} existing documents.")
        except Exception:
            print("Resume: No valid existing index found. Starting fresh.")

    # 2. 処理対象ファイルの収集
    files_to_process = []
    skipped_count = 0

    print("Scanning files...")
    for file_path in root_path.rglob('*'):
        if not file_path.is_file():
            continue
        if file_path.name.startswith('.'):
            continue
        if file_path.suffix.lower() not in {'.md', '.markdown', '.html', '.htm', '.txt', '.pdf'}:
            continue

        rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")

        # 既にEmbedding済みならスキップ
        if rel_path in existing_docs and 'embedding' in existing_docs[rel_path]:
            skipped_count += 1
            continue

        files_to_process.append((file_path, rel_path))

    if not files_to_process:
        print("All files are already processed! Nothing to do.")
        return

    print(f"New files to process: {len(files_to_process)} (Skipped: {skipped_count})")

    # 3. Embedding実行
    generator = LocalEmbeddingGenerator()
    new_docs_map = existing_docs.copy()

    batch_docs = []
    batch_texts = []

    total_files = len(files_to_process)

    for i, (file_path, rel_path) in enumerate(files_to_process):
        title, text = extract_text_from_file(file_path)

        if not text:
            print(f"Skipping empty: {rel_path}")
            continue

        if len(text) > Config.MAX_TEXT_LENGTH:
            text = text[:Config.MAX_TEXT_LENGTH]

        doc_id = sanitize_filename(rel_path)
        doc = {
            "id": doc_id,
            "title": title or file_path.stem,
            "source": rel_path,
            "text": text
        }

        batch_docs.append(doc)
        batch_texts.append(text)

        # バッチ実行判定 (バッチサイズ到達 or 最終ファイル)
        if len(batch_docs) >= Config.BATCH_SIZE or i == total_files - 1:
            if not batch_docs:
                continue

            # 生成
            vectors = generator.generate_batch(batch_texts)

            # 格納
            for d, vec in zip(batch_docs, vectors):
                d['embedding'] = vec
                new_docs_map[d['source']] = d

            # 進捗表示
            print(f"Processed: {i+1}/{total_files} files")

            # 定期保存
            current_batch_idx = i // Config.BATCH_SIZE
            if current_batch_idx > 0 and current_batch_idx % Config.SAVE_INTERVAL == 0:
                save_json(new_docs_map, output_path)

            batch_docs = []
            batch_texts = []

    # 最終保存
    save_json(new_docs_map, output_path)
    print(f"\nCompleted! Total documents in index: {len(new_docs_map)}")


def save_json(data_map: Dict[str, Any], path: str):
    """安全なJSON保存 (一時ファイル経由)"""
    data_list = list(data_map.values())
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)

        if os.path.exists(path):
            os.remove(path)
        os.rename(tmp_path, path)
        print("  (Index Auto-Saved)")
    except Exception as e:
        print(f"  [Error] Failed to save JSON: {e}")


def main():
    parser = argparse.ArgumentParser(description="RAG Index Builder (Hybrid/Final)")
    parser.add_argument("--root", "-r", default=".", help="Root directory")
    parser.add_argument("--out", "-o", default="rag_index_local.json", help="Output file")
    args = parser.parse_args()

    try:
        build_index(args.root, args.out)
    except KeyboardInterrupt:
        print("\nInterrupted by user. Progress saved.")
        sys.exit(0)

if __name__ == "__main__":
    main()
