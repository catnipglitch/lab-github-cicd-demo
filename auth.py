"""Auth0 認証モジュール - ServerClient の条件付き初期化。"""

import os


# Auth0 環境変数が設定されている場合のみ初期化
auth0_domain = os.getenv("AUTH0_DOMAIN")
auth0_client: object | None = None

if auth0_domain:
    from auth0_server_python.auth_server.server_client import ServerClient

    class MemoryStateStore:
        """インメモリ state store（開発用）。"""

        def __init__(self) -> None:
            self._data: dict = {}

        async def get(self, key: str, options: dict | None = None) -> object | None:
            return self._data.get(key)

        async def set(
            self, key: str, value: object, options: dict | None = None
        ) -> None:
            self._data[key] = value

        async def delete(self, key: str, options: dict | None = None) -> None:
            self._data.pop(key, None)

        async def delete_by_logout_token(
            self, claims: dict, options: dict | None = None
        ) -> None:
            pass

    class MemoryTransactionStore:
        """インメモリ transaction store（開発用）。"""

        def __init__(self) -> None:
            self._data: dict = {}

        async def get(self, key: str, options: dict | None = None) -> object | None:
            return self._data.get(key)

        async def set(
            self, key: str, value: object, options: dict | None = None
        ) -> None:
            self._data[key] = value

        async def delete(self, key: str, options: dict | None = None) -> None:
            self._data.pop(key, None)

    state_store = MemoryStateStore()
    transaction_store = MemoryTransactionStore()

    auth0_client = ServerClient(
        domain=auth0_domain,
        client_id=os.getenv("AUTH0_CLIENT_ID", ""),
        client_secret=os.getenv("AUTH0_CLIENT_SECRET", ""),
        secret=os.getenv("AUTH0_SECRET", ""),
        redirect_uri=os.getenv("AUTH0_REDIRECT_URI", "http://localhost:5000/callback"),
        state_store=state_store,
        transaction_store=transaction_store,
        authorization_params={"scope": "openid profile email"},
    )
