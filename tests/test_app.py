"""Flask アプリケーションのテスト。"""

import json
import os
import sys
from pathlib import Path

import pytest


@pytest.fixture
def client():
    """Flask テストクライアントを作成する。"""
    # 環境変数をクリーンにして Sentry 初期化を防ぐ
    env_backup = os.environ.copy()
    if "SENTRY_DSN" in os.environ:
        del os.environ["SENTRY_DSN"]

    # テスト用のビルド情報を設定
    os.environ["BUILD_TIME"] = "2024-01-01T00:00:00Z"
    os.environ["GIT_BRANCH"] = "test-branch"
    os.environ["GIT_COMMIT_SHA"] = "abc123def456"
    os.environ["GITHUB_RUN_ID"] = "12345"
    os.environ["GITHUB_RUN_NUMBER"] = "42"

    # app.py を動的にインポート（環境変数設定後）
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # 既にインポートされている場合は削除してリフレッシュ
    if "app" in sys.modules:
        del sys.modules["app"]

    import app as flask_app

    flask_app.app.config["TESTING"] = True

    with flask_app.app.test_client() as test_client:
        yield test_client

    # 環境変数を復元
    os.environ.clear()
    os.environ.update(env_backup)


def test_index_route_returns_200(client):
    """メインページが 200 を返すことを確認する。"""
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    """ヘルスチェックエンドポイントが正常に動作することを確認する。"""
    response = client.get("/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "ok"
    assert data["service"] == "github-cicd-demo"


def test_api_info_endpoint(client):
    """JSON API が正しい情報を返すことを確認する。"""
    response = client.get("/api/info")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["git_branch"] == "test-branch"
    assert data["git_commit_short"] == "abc123de"
    assert data["github_run_number"] == "42"
    assert data["sentry_enabled"] is False  # テストでは Sentry は無効


def test_logo_image_referenced(client):
    """HTML に logo.png が含まれていることを確認する。"""
    response = client.get("/")
    assert b"logo.png" in response.data


def test_build_info_displayed(client):
    """ビルド情報が表示されることを確認する。"""
    response = client.get("/")
    html = response.data.decode("utf-8")

    assert "test-branch" in html
    assert "abc123de" in html  # git_commit_short
    assert "42" in html  # github_run_number
    assert "2024-01-01T00:00:00Z" in html  # build_time
