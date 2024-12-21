FROM debian:bookworm-slim

WORKDIR /app

# 基本的なビルドツールとPythonの依存関係をインストール
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# コピー
COPY . .

# uvのインストールとPythonのセットアップ
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="$HOME/.local/bin:$PATH" && \
    uv sync && \
    uv pip install -e .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# アプリケーションの実行
CMD ["/app/.venv/bin/python", "main.py"]
