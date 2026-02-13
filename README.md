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

### 1. 仮想環境の作成

プロジェクトの依存パッケージをシステムの Python から分離するため、仮想環境を作成します。

```bash
python3 -m venv venv
```

これにより `venv/` ディレクトリが作成され、プロジェクト専用の Python 環境が用意されます。

### 2. 仮想環境の有効化

```bash
source venv/bin/activate
```

有効化するとプロンプトに `(venv)` が表示されます。以降のコマンドはすべてこの仮想環境内で実行してください。

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. API キーの設定

`.env` ファイルを作成して Gemini API キーを設定します。

```
GOOGLE_API_KEY=your_api_key_here
```

API キーは [Google AI Studio](https://aistudio.google.com/apikey) から取得できます。

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
