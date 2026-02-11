# マルチステージビルド: 依存関係のインストール
FROM python:3.13-slim AS builder

WORKDIR /app

# uv をインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係ファイルをコピー
COPY pyproject.toml uv.lock ./

# 本番用依存関係のみをインストール
RUN uv sync --frozen --no-dev

# ランタイムステージ: 実行環境
FROM python:3.13-slim

WORKDIR /app

# ビルド引数（GitHub Actions から渡される）
ARG BUILD_TIME
ARG GIT_BRANCH
ARG GIT_COMMIT_SHA
ARG GITHUB_RUN_ID
ARG GITHUB_RUN_NUMBER

# ビルド引数を環境変数に変換
ENV BUILD_TIME=${BUILD_TIME} \
    GIT_BRANCH=${GIT_BRANCH} \
    GIT_COMMIT_SHA=${GIT_COMMIT_SHA} \
    GITHUB_RUN_ID=${GITHUB_RUN_ID} \
    GITHUB_RUN_NUMBER=${GITHUB_RUN_NUMBER} \
    PORT=8080 \
    PYTHONUNBUFFERED=1

# builder から仮想環境をコピー
COPY --from=builder /app/.venv /app/.venv

# アプリケーションコードをコピー
COPY app.py ./
COPY templates ./templates
COPY pyproject.toml ./

# 静的ファイル（ロゴ）をコピー
COPY images/logo.png ./static/images/logo.png

# 仮想環境の Python を PATH に追加
ENV PATH="/app/.venv/bin:$PATH"

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health').read()"

# gunicorn で起動（1 worker, 8 threads）
CMD gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
