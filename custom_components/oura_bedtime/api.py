"""Oura Ring API client."""

from __future__ import annotations

import aiohttp

from .const import API_BASE_URL, LOGGER


class OuraApiError(Exception):
    """Base exception for Oura API errors."""


class OuraApiAuthenticationError(OuraApiError):
    """Authentication error."""


class OuraApiCommunicationError(OuraApiError):
    """Communication error."""


class OuraApiClient:
    """Async client for the Oura Ring API."""

    def __init__(self, token: str, session: aiohttp.ClientSession) -> None:
        self._token = token
        self._session = session

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    async def async_validate_token(self) -> bool:
        """Validate the access token by making a lightweight API call."""
        await self._api_wrapper(
            f"{API_BASE_URL}/usercollection/personal_info"
        )
        return True

    async def async_get_sleep(
        self, start_date: str, end_date: str
    ) -> list[dict]:
        """Fetch sleep session data for a date range."""
        url = (
            f"{API_BASE_URL}/usercollection/sleep"
            f"?start_date={start_date}&end_date={end_date}"
        )
        response = await self._api_wrapper(url)
        return [
            r for r in response.get("data", [])
            if r.get("type") == "long_sleep"
        ]

    async def _api_wrapper(self, url: str) -> dict:
        """Make an API request with error handling."""
        try:
            async with self._session.get(
                url,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status in (401, 403):
                    raise OuraApiAuthenticationError(
                        "Invalid or expired access token"
                    )
                if resp.status != 200:
                    raise OuraApiError(
                        f"Oura API returned status {resp.status}"
                    )
                return await resp.json()
        except OuraApiError:
            raise
        except aiohttp.ClientError as err:
            raise OuraApiCommunicationError(
                f"Error communicating with Oura API: {err}"
            ) from err
        except TimeoutError as err:
            raise OuraApiCommunicationError(
                "Timeout connecting to Oura API"
            ) from err
