# RAG Chat

Webページを読み込んで質問に答える RAG（Retrieval-Augmented Generation）チャットアプリケーション。

## 概要

URLを登録すると、Webページの内容をチャンク分割してベクトルDBに保存し、質問に対して関連する情報を検索してLLMが回答を生成します。

## 技術構成

| コンポーネント | 技術 |
|---|---|
| Web UI | Flask + HTML/CSS/JS |
| ベクトルストア | ChromaDB |
| Embedding | Gemini REST API (`gemini-embedding-001`) |
| LLM | Gemini REST API (`gemini-2.0-flash-lite`) |
| 文書読み込み | LangChain `WebBaseLoader` |

## ファイル構成

```
RAG/
├── app.py            # Flask Webサーバー（API: /api/ask, /api/index）
├── rag.py            # RAGコアロジック（インデックス作成・質問応答）
├── requirements.txt  # 依存パッケージ
├── templates/
│   └── index.html    # チャットUI
├── static/
│   └── style.css     # スタイル
└── .env              # GOOGLE_API_KEY（要作成）
```

## セットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` ファイルを作成して Gemini API キーを設定：

```
GOOGLE_API_KEY=your_api_key_here
```

## 使い方

### Web UI

```bash
python3 app.py
```

`http://localhost:5000` にアクセスし、URLを登録してからチャットで質問。

### CLI

```bash
# Webページをインデックスに追加
python3 rag.py index https://example.com

# 質問する
python3 rag.py ask "このページの内容は？"
```
