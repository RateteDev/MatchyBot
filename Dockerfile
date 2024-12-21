FROM python:3.12-slim

WORKDIR /app

# 依存関係のファイルをコピー
COPY pyproject.toml uv.lock ./

# 必要なパッケージをインストール
RUN pip install --no-cache-dir uv && \
    uv pip install --system

# アプリケーションのソースコードをコピー
COPY . .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# アプリケーションの実行
CMD ["python", "main.py"]
