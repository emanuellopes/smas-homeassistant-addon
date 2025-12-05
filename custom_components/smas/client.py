from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import asyncio

import aiohttp
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGIN_URL


@dataclass
class AuthInfo:
    """Container for authentication information."""

    token: Optional[str]
    header_name: str
    expiration: Optional[int]
    cookies: Dict[str, str]


class SmasClient:
    """Client for communicating with the SMAS Leiria portal."""

    def __init__(self, hass: HomeAssistant, username: str, password: str) -> None:
        """Initialize the client with credentials."""
        self._hass = hass
        self._username = username
        self._password = password
        self._session = async_get_clientsession(hass)

        self._token: Optional[str] = None
        self._header_name: str = "X-Auth-Token"  # default, will be overwritten by API
        self._expiration: Optional[int] = None
        self._cookies: Dict[str, str] = {}

    @property
    def token(self) -> Optional[str]:
        """Return the current auth token."""
        return self._token

    @property
    def header_name(self) -> str:
        """Return the header name used to send the token."""
        return self._header_name

    @property
    def cookies(self) -> Dict[str, str]:
        """Return the current cookies."""
        return self._cookies

    @property
    def expiration(self) -> Optional[int]:
        """Return the token expiration timestamp (epoch ms)."""
        return self._expiration

    async def async_login(self) -> AuthInfo:
        """Perform login and store token/cookies.

        Raises:
            aiohttp.ClientError / asyncio.TimeoutError on network issues
            RuntimeError if authentication fails or no token is returned

        Returns:
            AuthInfo with token, header_name, expiration and cookies.
        """
        async with async_timeout.timeout(15):
            response = await self._session.post(
                LOGIN_URL,
                json={
                    "username": self._username,
                    "password": self._password,
                },
            )

        if response.status != 200:
            text = await response.text()
            raise RuntimeError(f"Authentication failed ({response.status}): {text}")

        # Extract cookies from the response
        self._cookies = {k: v.value for k, v in response.cookies.items()}

        data: Any = await response.json(content_type=None)

        # Expecting top-level keys: "user", "token", "currency"
        if not isinstance(data, dict) or "token" not in data:
            raise RuntimeError("Authentication response does not contain 'token' object")

        token_block = data["token"]
        if not isinstance(token_block, dict):
            raise RuntimeError("Invalid 'token' structure in response")

        token = token_block.get("token")
        header_name = token_block.get("authHeaderName") or "X-Auth-Token"
        expiration = token_block.get("expirationDate")

        if not token:
            raise RuntimeError("Authentication response does not contain a token value")

        self._token = token
        self._header_name = header_name
        self._expiration = expiration

        return AuthInfo(
            token=self._token,
            header_name=self._header_name,
            expiration=self._expiration,
            cookies=self._cookies,
        )

    async def async_request(
        self,
        method: str
