#!/usr/bin/env python3
"""
build_rag_index.py

ワークスペース内のMarkdown/HTML/TXTファイルを走査してテキストを抽出し、
簡易RAGインデックス（rag_index.json）を生成します。

使い方:
  python scripts/build_rag_index.py --root . --out rag_index.json

"""

import os
import argparse
import json
import re
import warnings
import logging
import sys
from html.parser import HTMLParser

try:
    import google.generativeai as genai

    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

warnings.filterwarnings("ignore")

# Suppress PDF library warnings
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("pypdf").setLevel(logging.ERROR)
logging.getLogger("pdfplumber.pdf").setLevel(logging.ERROR)
logging.getLogger("pikepdf").setLevel(logging.ERROR)

# Suppress stderr output from PDF libraries
_stderr_backup = sys.stderr
sys.stderr = open(os.devnull, "w")

try:
    import pdfplumber  # type: ignore

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

EXTS = {".md", ".markdown", ".html", ".htm", ".txt", ".pdf"}


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._texts = []
        self._skip = False
        self._skip_tags = {"script", "style"}

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


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "doc"


def get_embedding(text, api_key=None):
    """Generate embedding using Gemini Embeddings API."""
    if not HAS_GENAI or not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        result = genai.embed_content(model="models/embedding-001", content=text)
        return result["embedding"]
    except Exception as e:
        sys.stderr = _stderr_backup
        print(f"      Embedding error: {e}")
        sys.stderr = open(os.devnull, "w")
        return None


def extract_title_from_md(text):
    for line in text.splitlines():
        m = re.match(r"#{1,6}\s*(.+)", line)
        if m:
            return m.group(1).strip()
    # fallback first non-empty line
    for line in text.splitlines():
        if line.strip():
            return line.strip()[:120]
    return None


def extract_title_from_html(text):
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    # fallback: first h1
    m2 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
    if m2:
        return re.sub(r"<[^>]+>", "", m2.group(1)).strip()
    return None


def extract_text(path, ext):
    # PDF extraction
    if ext == ".pdf":
        if not HAS_PDFPLUMBER:
            return None, None
        try:
            texts = []
            with pdfplumber.open(path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    t = page.extract_text()
                    if t:
                        texts.append(t)
            if not texts:
                return os.path.basename(path), None
            text = " ".join(texts)
            title = os.path.basename(path)
        except Exception as e:
            print(f"      PDF ERROR: {e}")
            return None, None
    else:
        # Text-based formats
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
        except Exception:
            return None, None

        if ext in (".html", ".htm"):
            title = extract_title_from_html(raw)
            parser = HTMLTextExtractor()
            parser.feed(raw)
            text = parser.get_text()
        else:
            title = extract_title_from_md(raw) if ext in (".md", ".markdown") else None
            text = raw

    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 10000:
        text = text[:10000]
    if title:
        title = re.sub(r"\s+", " ", title).strip()
    return title, text


def build_index(root, api_key=None):
    docs = []
    root = os.path.abspath(root)
    print(f"Scanning: {root}")
    print(
        f"PDF support: {'enabled (pdfplumber installed)' if HAS_PDFPLUMBER else 'disabled (pdfplumber not installed)'}"
    )
    print(
        f"Embedding support: {'enabled (google-generativeai installed)' if HAS_GENAI else 'disabled (google-generativeai not installed)'}\n"
    )

    for dirpath, dirnames, filenames in os.walk(root):
        # skip hidden and common large folders
        if any(
            part.startswith(".")
            for part in os.path.relpath(dirpath, root).split(os.sep)
        ):
            continue
        for fn in filenames:
            name, ext = os.path.splitext(fn)
            ext = ext.lower()
            if ext not in EXTS:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")
            title, text = extract_text(full, ext)
            if not text:
                print(f"  ✗ {rel} (empty or failed to extract)")
                continue
            doc_id = slugify(rel)
            doc = {"id": doc_id, "title": title or name, "source": rel, "text": text}

            # Generate embedding if API key provided
            if api_key and HAS_GENAI:
                embedding = get_embedding(
                    text[:2000], api_key
                )  # Use first 2000 chars for embedding
                if embedding:
                    doc["embedding"] = embedding
                    print(f"  ✓ {rel} ({len(text)} chars, embedded)")
                else:
                    print(f"  ✓ {rel} ({len(text)} chars, no embedding)")
            else:
                print(f"  ✓ {rel} ({len(text)} chars)")

            docs.append(doc)

    return docs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-r", default=".", help="root path to scan")
    parser.add_argument(
        "--out", "-o", default="rag_index.json", help="output json file"
    )
    parser.add_argument(
        "--api-key", "-k", default=None, help="Gemini API key for embeddings (optional)"
    )
    args = parser.parse_args()

    docs = build_index(args.root, args.api_key)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"✓ Found {len(docs)} documents, writing {args.out}")


if __name__ == "__main__":
    main()
