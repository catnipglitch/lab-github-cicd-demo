"""Flask Web アプリケーション - ビルド情報とロゴを表示するシンプルな Web UI。"""

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from sentry_sdk.integrations.flask import FlaskIntegration


def _get_sentry_dsn() -> str | None:
    """実行環境に応じて Sentry DSN を決定する（main.py と同じパターン）。"""
    in_codespaces = bool(os.getenv("CODESPACES") or os.getenv("CODESPACE_NAME"))
    if not in_codespaces:
        env_file = Path(__file__).resolve().parent / ".env"
        load_dotenv(env_file, override=False)

    return os.getenv("SENTRY_DSN")


# Sentry 初期化
dsn = _get_sentry_dsn()
if dsn:
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
        integrations=[FlaskIntegration()],
    )


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_build_info() -> dict:
    """ビルド情報を環境変数から取得する。"""
    return {
        "build_time": os.getenv("BUILD_TIME", "Not set"),
        "git_branch": os.getenv("GIT_BRANCH", "unknown"),
        "git_commit_sha": os.getenv("GIT_COMMIT_SHA", "unknown"),
        "git_commit_short": os.getenv("GIT_COMMIT_SHA", "unknown")[:8],
        "github_run_id": os.getenv("GITHUB_RUN_ID", "N/A"),
        "github_run_number": os.getenv("GITHUB_RUN_NUMBER", "N/A"),
        "python_version": sys.version.split()[0],
        "sentry_enabled": dsn is not None,
        "deploy_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "k_service": os.getenv("K_SERVICE", "N/A"),
        "k_revision": os.getenv("K_REVISION", "N/A"),
    }


@app.route("/")
def index():
    """メインページ - ロゴとビルド情報を表示。"""
    build_info = get_build_info()
    return render_template("index.html", build_info=build_info)


@app.route("/health")
def health():
    """ヘルスチェックエンドポイント（Cloud Run 用）。"""
    return jsonify({"status": "ok", "service": "github-cicd-demo"}), 200


@app.route("/api/info")
def api_info():
    """ビルド情報を JSON で返す API エンドポイント。"""
    build_info = get_build_info()
    return jsonify(build_info)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Sentry enabled: {dsn is not None}")
    app.run(host="0.0.0.0", port=port, debug=False)
