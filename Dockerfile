FROM debian:bookworm-slim

WORKDIR /app

# 基本的なビルドツールとPythonの依存関係をインストール
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uvのインストールとPythonのセットアップ
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のファイルをコピー
COPY pyproject.toml uv.lock ./

# uvを使用してパッケージをインストール
RUN uv sync
RUN uv pip install -e .

# アプリケーションのソースコードをコピー
COPY . .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# アプリケーションの実行
CMD ["python", "main.py"]
