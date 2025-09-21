from typing import Dict, Optional

import requests
from requests import Response

LOGIN_ENDPOINT_TEMPLATE = "{}/api/v1/login"
NAMES_ENDPOINT_TEMPLATE = "{}/api/v1/names"

Identities = Dict[int, str]


class UrchinClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._login_endpoint = LOGIN_ENDPOINT_TEMPLATE.format(base_url)
        self._names_endpoint = NAMES_ENDPOINT_TEMPLATE.format(base_url)

        self._credentials = {"username": username, "password": password}

        self._token: Optional[str] = None
        self._server_identities: Dict[int, Identities] = {}

    def _get_token(self) -> str:
        if not self._token:
            resp = requests.post(self._login_endpoint, json=self._credentials)

            if resp.status_code != requests.codes.ok:
                resp.raise_for_status()

            self._token = resp.json()["token"]

        return self._token

    def _send_request(self, guild_id: int) -> Response:
        token = self._get_token()

        return requests.get(
            self._names_endpoint,
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
