#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
query_rag.py (Hybrid RAG)

1. ユーザーの質問をローカルモデル(E5)でベクトル化
2. ローカルのrag_index_local.jsonから関連文書を検索 (Retrieve)
3. Gemini APIに検索結果を渡して回答を生成 (Generate)
"""

import json
import argparse
import numpy as np

# === 設定 ===
# 検索用ローカルモデル (インデックス作成時と同じものを使用)
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
# E5モデルは検索クエリに "query: " を付けるルールがある
QUERY_PREFIX = "query: "

# 回答生成用クラウドモデル
GENERATION_MODEL_NAME = "gemini-1.5-flash"

try:
    import google.generativeai as genai
    from sentence_transformers import SentenceTransformer # type: ignore
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    print("Error: 必要なライブラリが見つかりません。")
    print("pip install google-generativeai sentence-transformers scikit-learn")
    exit(1)


class RAGChatbot:
    def __init__(self, index_path, api_key):
        # 1. ローカル検索モデルの準備
        print(f"Loading local search model: {EMBEDDING_MODEL_NAME}...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # 2. インデックスの読み込み
        print(f"Loading index from {index_path}...")
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)

            # 検索を高速化するためにベクトルだけ抽出してnumpy配列にする
            self.doc_vectors = np.array([doc["embedding"] for doc in self.documents])
            print(f"Loaded {len(self.documents)} documents.")

        except FileNotFoundError:
            print(
                f"Error: {index_path} が見つかりません。先に build_rag_index_final.py を実行してください。"
            )
            exit(1)

        # 3. Gemini APIの準備 (回答生成用)
        genai.configure(api_key=api_key)
        self.generator = genai.GenerativeModel(GENERATION_MODEL_NAME)

    def search(self, query, top_k=3):
        """質問に関連するドキュメントを検索する (Retrieve)"""
        # E5モデル用にプレフィックスを付与してベクトル化
        query_text = QUERY_PREFIX + query
        query_vector = self.embedder.encode(query_text, convert_to_numpy=True).reshape(
            1, -1
        )

        # コサイン類似度で検索
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]

        # スコアが高い順にインデックスを取得
        top_indices = similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            score = similarities[idx]
            doc = self.documents[idx]
            results.append(
                {
                    "score": score,
                    "source": doc["source"],
                    "text": doc["text"],
                    "title": doc["title"],
                }
            )
        return results

    def generate_answer(self, query, context_docs):
        """検索結果を元にGeminiで回答を作成する (Generate)"""

        # コンテキスト（参考資料）テキストを作成
        context_text = ""
        for i, doc in enumerate(context_docs, 1):
            context_text += (
                f"\n--- 資料 {i} (Source: {doc['source']}) ---\n{doc['text'][:2000]}\n"
            )

        # プロンプト（AIへの指示書）
        prompt = f"""
あなたは優秀なアシスタントです。以下の「参考資料」だけに基づいて、ユーザーの質問に答えてください。
もし資料に答えがない場合は、正直に「資料には情報がありません」と答えてください。
事実を捏造してはいけません。

【質問】
{query}

【参考資料】
{context_text}

【回答】
"""
        # Geminiに生成させる
        response = self.generator.generate_content(prompt)
        return response.text

    def chat_loop(self):
        print("\n" + "=" * 50)
        print("RAG Chatbot (Hybrid: Local Search + Gemini Answer)")
        print("Type 'exit' or 'quit' to stop.")
        print("=" * 50 + "\n")

        while True:
            user_input = input("\nあなた: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            if not user_input.strip():
                continue

            print(" (検索中...)")
            # 1. 検索
            results = self.search(user_input, top_k=3)

            # 検索結果のソースを表示（デバッグ用）
            print(f" [参照] {results[0]['source']} (Score: {results[0]['score']:.4f})")

            print(" (Geminiが回答を生成中...)")
            # 2. 生成
            try:
                answer = self.generate_answer(user_input, results)
                print(f"\nAI: {answer}")
            except Exception as e:
                print(f"\nError: Gemini APIのエラーが発生しました。\n{e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index", default="rag_index_local.json", help="Path to the index file"
    )
    parser.add_argument("--api-key", required=True, help="Google Gemini API Key")
    args = parser.parse_args()

    bot = RAGChatbot(args.index, args.api_key)
    bot.chat_loop()


if __name__ == "__main__":
    main()
