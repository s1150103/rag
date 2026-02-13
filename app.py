#!/usr/bin/env python3
"""RAG Web アプリケーション"""

from flask import Flask, render_template, request, jsonify
from rag import index_url, ask_question

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "質問が空です"}), 400
    try:
        answer = ask_question(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/index", methods=["POST"])
def api_index():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "URLが空です"}), 400
    try:
        chunk_count = index_url(url)
        return jsonify({"message": f"インデックス完了: {chunk_count} チャンクを保存しました"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
