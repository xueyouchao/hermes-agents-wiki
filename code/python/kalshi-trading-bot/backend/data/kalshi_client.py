"""Kalshi API client with RSA-PSS signature authentication.

Uses a shared httpx.AsyncClient session for connection pooling.
Implements exponential backoff on rate limits (429) and server errors (5xx).
"""
import asyncio
import base64
import hashlib
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from backend.config import settings

logger = logging.getLogger("trading_bot")

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0
RATE_LIMIT_EXTRA_WAIT = 5.0  # Extra wait on 429


class KalshiClient:
    """Async Kalshi API client using RSA-PSS signature auth.

    Uses a shared httpx.AsyncClient for connection pooling.
    Implements exponential backoff on transient failures.
    """

    def __init__(self):
        self._private_key = None
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the shared HTTP client session."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(15.0, connect=5.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    async def close(self):
        """Close the shared HTTP client session."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _load_private_key(self):
        """Load RSA private key from file (lazy, cached)."""
        if self._private_key is not None:
            return self._private_key

        key_path = settings.KALSHI_PRIVATE_KEY_PATH
        if not key_path:
            raise ValueError("KALSHI_PRIVATE_KEY_PATH not configured")

        pem_data = Path(key_path).expanduser().read_bytes()
        self._private_key = serialization.load_pem_private_key(pem_data, password=None)
        return self._private_key

    def _sign_request(self, method: str, path: str) -> Dict[str, str]:
        """
        Generate auth headers for a Kalshi API request.

        Signature = RSA-PSS-sign(timestamp_ms + METHOD + path)
        where path = /trade-api/v2/... (no query params).
        """
        timestamp_ms = str(int(time.time() * 1000))
        message = f"{timestamp_ms}{method.upper()}{path}"

        private_key = self._load_private_key()
        signature = private_key.sign(
            message.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        return {
            "KALSHI-ACCESS-KEY": settings.KALSHI_API_KEY_ID,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode("utf-8"),
            "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
            "Content-Type": "application/json",
        }

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request with exponential backoff on transient failures.

        Retries on:
        - 429 (rate limit)
        - 500, 502, 503, 504 (server errors)
        - Connection errors
        """
        client = await self._get_client()
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(MAX_RETRIES + 1):
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, **kwargs)
                elif method == "POST":
                    response = await client.post(url, headers=headers, **kwargs)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                # Success — return
                if response.status_code < 400:
                    return response

                # Rate limited — backoff longer
                if response.status_code == 429:
                    if attempt < MAX_RETRIES:
                        wait = backoff + RATE_LIMIT_EXTRA_WAIT
                        logger.warning(
                            f"Rate limited (429) on {url}, retrying in {wait:.1f}s "
                            f"(attempt {attempt + 1}/{MAX_RETRIES})"
                        )
                        await asyncio.sleep(wait)
                        backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)
                        continue

                # Server errors — retry
                if response.status_code >= 500 and attempt < MAX_RETRIES:
                    logger.warning(
                        f"Server error {response.status_code} on {url}, "
                        f"retrying in {backoff:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})"
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)
                    continue

                # Client error (4xx, not 429) — don't retry
                response.raise_for_status()
                return response

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt < MAX_RETRIES:
                    logger.warning(
                        f"Connection error on {url}: {e}, "
                        f"retrying in {backoff:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})"
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)
                    continue
                raise

        # Shouldn't reach here, but if all retries exhausted
        response.raise_for_status()
        return response

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> dict:
        """
        Authenticated GET request to Kalshi API with retry.

        Args:
            path: API path after /trade-api/v2 (e.g., "/markets")
            params: Query parameters (not included in signature)
        """
        full_path = f"/trade-api/v2{path}"
        url = f"{BASE_URL}{path}"
        headers = self._sign_request("GET", full_path)

        response = await self._request_with_retry("GET", url, headers, params=params)
        return response.json()

    async def get_markets(self, params: Optional[Dict[str, Any]] = None) -> dict:
        """Fetch markets with optional filters."""
        return await self.get("/markets", params=params)

    async def get_market(self, ticker: str) -> dict:
        """Fetch a single market by ticker."""
        return await self.get(f"/markets/{ticker}")

    async def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> dict:
        """
        Authenticated POST request to Kalshi API with retry.

        Args:
            path: API path after /trade-api/v2 (e.g., "/portfolio/orders")
            json: JSON body payload
        """
        full_path = f"/trade-api/v2{path}"
        url = f"{BASE_URL}{path}"
        headers = self._sign_request("POST", full_path)

        response = await self._request_with_retry("POST", url, headers, json=json)
        return response.json()

    async def delete(self, path: str) -> dict:
        """
        Authenticated DELETE request to Kalshi API with retry.

        Args:
            path: API path after /trade-api/v2
        """
        full_path = f"/trade-api/v2{path}"
        url = f"{BASE_URL}{path}"
        headers = self._sign_request("DELETE", full_path)

        response = await self._request_with_retry("DELETE", url, headers)
        return response.json()

    async def get_balance(self) -> dict:
        """Get portfolio balance (useful for auth test)."""
        return await self.get("/portfolio/balance")


def kalshi_credentials_present() -> bool:
    """Check if Kalshi API credentials are configured."""
    return bool(settings.KALSHI_API_KEY_ID and settings.KALSHI_PRIVATE_KEY_PATH)