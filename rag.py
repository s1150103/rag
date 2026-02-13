#!/usr/bin/env python3
"""RAGシステム - Webページをデータソースとした質問応答"""

import os
import sys

from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault("USER_AGENT", "RAG-Bot/1.0")

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import time
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

CHROMA_DIR = "./chroma_db"
GEMINI_MODEL = "gemini-2.0-flash-lite"
GEMINI_EMBED_MODEL = "gemini-embedding-001"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _gemini_api_key():
    return os.environ["GOOGLE_API_KEY"]


def _request_with_retry(url, json_body, max_retries=5):
    """リトライ付きHTTP POST（429レート制限対応）"""
    for attempt in range(max_retries):
        resp = requests.post(url, json=json_body)
        if resp.status_code == 429:
            wait = 4 * (attempt + 1)
            print(f"  レート制限、{wait}秒待機中...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()


class GeminiEmbeddings:
    """Gemini REST API を使った Embedding クラス（ChromaDB互換）"""

    def _batch_embed(self, texts):
        """バッチAPIでEmbedding"""
        url = f"{GEMINI_API_BASE}/models/{GEMINI_EMBED_MODEL}:batchEmbedContents?key={_gemini_api_key()}"
        req_list = [{"model": f"models/{GEMINI_EMBED_MODEL}", "content": {"parts": [{"text": t}]}} for t in texts]
        resp = _request_with_retry(url, {"requests": req_list})
        return [e["values"] for e in resp.json()["embeddings"]]

    def embed_documents(self, texts):
        results = []
        batch_size = 20
        total_batches = (len(texts) + batch_size - 1) // batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"  Embedding {i // batch_size + 1}/{total_batches}...")
            results.extend(self._batch_embed(batch))
            if i + batch_size < len(texts):
                time.sleep(2)
        return results

    def embed_query(self, text):
        return self._batch_embed([text])[0]


def get_vectorstore():
    """ChromaDBベクトルストアを取得"""
    embeddings = GeminiEmbeddings()
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)


def index_url(url: str):
    """Webページをインデックスに追加"""
    print(f"読み込み中: {url}")
    loader = WebBaseLoader(url)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    chunks = splitter.split_documents(docs)
    print(f"チャンク数: {len(chunks)}")

    vectorstore = get_vectorstore()
    # 全チャンクを一括登録（Embedding はバッチAPIで一括処理される）
    vectorstore.add_documents(chunks)
    print(f"インデックス完了: {len(chunks)} チャンクを保存しました")
    return len(chunks)


def ask_question(question: str):
    """質問に対して回答を生成"""
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    print("回答を生成中...")
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""以下のコンテキストに基づいて質問に答えてください。
コンテキストに答えがない場合は「情報が見つかりませんでした」と答えてください。

コンテキスト:
{context}

質問: {question}

回答:"""

    url = f"{GEMINI_API_BASE}/models/{GEMINI_MODEL}:generateContent?key={_gemini_api_key()}"
    resp = _request_with_retry(url, {"contents": [{"parts": [{"text": prompt}]}]})
    answer = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    print(f"\n{answer}")
    return answer


def main():
    if len(sys.argv) < 3:
        print("使い方:")
        print("  python3 rag.py index <URL>       - Webページをインデックスに追加")
        print('  python3 rag.py ask "<質問>"       - 質問して回答を取得')
        sys.exit(1)

    command = sys.argv[1]

    if command == "index":
        index_url(sys.argv[2])
    elif command == "ask":
        ask_question(sys.argv[2])
    else:
        print(f"不明なコマンド: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
