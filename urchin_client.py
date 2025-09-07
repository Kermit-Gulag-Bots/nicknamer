from typing import Dict, Optional

import requests
from requests import Response

ENDPOINT_BASE_URL = "https://nicknamer-server-production.up.railway.app"
LOGIN_ENDPOINT = f"{ENDPOINT_BASE_URL}/api/v1/login"
NAMES_ENDPOINT = f"{ENDPOINT_BASE_URL}/api/v1/names"

Identities = Dict[int, str]


class UrchinClient:
    def __init__(self, username: str, password: str) -> None:
        self._credentials = {"username": username, "password": password}

        self._token: Optional[str] = None
        self._server_identities: Dict[int, Identities] = {}

    def _get_token(self) -> str:
        if not self._token:
            resp = requests.post(LOGIN_ENDPOINT, json=self._credentials)

            if resp.status_code != requests.codes.ok:
                resp.raise_for_status()

            self._token = resp.json()["token"]

        return self._token

    def _send_request(self, guild_id: int) -> Response:
        token = self._get_token()

        return requests.get(
            NAMES_ENDPOINT,
            headers={"authorization": f"Bearer {token}"},
            params={"server_id": str(guild_id)},
        )

    def _refresh_identities(self, guild_id: int) -> None:
        resp = self._send_request(guild_id)

        if resp.status_code == requests.codes.unauthorized:
            # Could be expired token, ditch the token and try again
            self._token = None
            resp = self._send_request(guild_id)

        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        self._server_identities[guild_id] = {
            info["discord_id"]: info["name"] for info in resp.json()["names"]
        }

    def get_names(self, guild_id: int) -> Identities:
        if guild_id not in self._server_identities:
            self._refresh_identities(guild_id)

        return self._server_identities[guild_id]

    def get_name(self, guild_id: int, discord_id: int) -> str:
        if discord_id not in (identities := self.get_names(guild_id)):
            self._refresh_identities(guild_id)
            identities = self.get_names(guild_id)

        return identities[discord_id]
