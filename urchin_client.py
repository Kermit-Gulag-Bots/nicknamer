from typing import Dict, Optional

import requests

ENDPOINT_BASE_URL = "https://nicknamer-server-production.up.railway.app"
LOGIN_ENDPOINT = f"{ENDPOINT_BASE_URL}/api/v1/login"
NAMES_ENDPOINT = f"{ENDPOINT_BASE_URL}/api/v1/names"

Identities = Dict[int, str]

class UrchinClient:
    def __init__(self, username: str, password: str) -> None:
        self._credentials = {"username": username, "password": password}

        self._token: Optional[str] = None
        self._identities: Optional[Identities] = None

    def _get_token(self) -> str:
        if not self._token:
            resp = requests.post(LOGIN_ENDPOINT, json=self._credentials)

            if resp.status_code != requests.codes.ok:
                resp.raise_for_status()

            self._token = resp.json()["token"]

        return self._token

    def get_names(self) -> Identities:
        if not self._identities:
            token = self._get_token()

            resp = requests.get(
                NAMES_ENDPOINT, headers={"authorization": f"Bearer {token}"}
            )

            if resp.status_code != requests.codes.ok:
                resp.raise_for_status()

            self._identities = {
                info["discord_id"]: info["name"] for info in resp.json()["names"]
            }

        return self._identities

    def get_name(self, discord_id: int) -> str:
        return self.get_names()[discord_id]
