"""
LLM client for AidFinder.

Primary: OpenRouter (any model configured in .env)
Fallback: Qwen (DashScope)
If both are unavailable → returns None (caller uses conversation engine fallback)
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import requests

from app.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_MAX_TOKENS,
    OPENROUTER_MODEL,
    OPENROUTER_SITE_NAME,
    OPENROUTER_SITE_URL,
    OPENROUTER_TEMPERATURE,
    OPENROUTER_TIMEOUT_SECONDS,
    QWEN_API_KEY,
    QWEN_API_URL,
    QWEN_MAX_TOKENS,
    QWEN_MODEL,
    QWEN_TEMPERATURE,
    QWEN_TIMEOUT_SECONDS,
)


class LLMClient:
    """Unified LLM client: OpenRouter primary, Qwen fallback."""

    def __init__(self) -> None:
        self.openrouter_available = bool(OPENROUTER_API_KEY)
        self.qwen_available = bool(QWEN_API_KEY)

    @property
    def is_available(self) -> bool:
        return self.openrouter_available or self.qwen_available

    # ── Sync generation (used by non-streaming paths & fallback) ──────

    def generate(self, messages: list[dict]) -> str | None:
        response = self._call_openrouter(messages)
        if response is not None:
            return response
        return self._call_qwen(messages)

    # ── Async streaming generation ────────────────────────────────────

    async def generate_stream(
        self, messages: list[dict]
    ) -> AsyncStreamResult | None:
        """Return an AsyncStreamResult or None if no provider available."""
        if self.openrouter_available:
            stream = await self._call_openrouter_stream(messages)
            if stream is not None:
                return stream
        if self.qwen_available:
            stream = await self._call_qwen_stream(messages)
            if stream is not None:
                return stream
        return None

    # ── OpenRouter helpers ────────────────────────────────────────────

    def _call_openrouter(self, messages: list[dict]) -> str | None:
        if not self.openrouter_available:
            return None
        try:
            resp = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": OPENROUTER_SITE_URL,
                    "X-Title": OPENROUTER_SITE_NAME,
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": OPENROUTER_TEMPERATURE,
                    "max_tokens": OPENROUTER_MAX_TOKENS,
                },
                timeout=OPENROUTER_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return self._extract_content(resp.json())
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            return None

    async def _call_openrouter_stream(self, messages: list[dict]) -> AsyncStreamResult | None:
        if not self.openrouter_available:
            return None
        try:
            async with httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    OPENROUTER_API_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": OPENROUTER_SITE_URL,
                        "X-Title": OPENROUTER_SITE_NAME,
                    },
                    json={
                        "model": OPENROUTER_MODEL,
                        "messages": messages,
                        "temperature": OPENROUTER_TEMPERATURE,
                        "max_tokens": OPENROUTER_MAX_TOKENS,
                        "stream": True,
                    },
                ) as response:
                    if response.status_code != 200:
                        return None
                    return AsyncStreamResult(response=response, source="openrouter")
        except (httpx.HTTPError, Exception):
            return None

    # ── Qwen helpers ──────────────────────────────────────────────────

    def _call_qwen(self, messages: list[dict]) -> str | None:
        if not self.qwen_available:
            return None
        try:
            resp = requests.post(
                QWEN_API_URL,
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": QWEN_MODEL,
                    "messages": messages,
                    "temperature": QWEN_TEMPERATURE,
                    "max_tokens": QWEN_MAX_TOKENS,
                },
                timeout=QWEN_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return self._extract_content(resp.json())
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            return None

    async def _call_qwen_stream(self, messages: list[dict]) -> AsyncStreamResult | None:
        if not self.qwen_available:
            return None
        try:
            async with httpx.AsyncClient(timeout=QWEN_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    QWEN_API_URL,
                    headers={
                        "Authorization": f"Bearer {QWEN_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": QWEN_MODEL,
                        "messages": messages,
                        "temperature": QWEN_TEMPERATURE,
                        "max_tokens": QWEN_MAX_TOKENS,
                        "stream": True,
                    },
                ) as response:
                    if response.status_code != 200:
                        return None
                    return AsyncStreamResult(response=response, source="qwen")
        except (httpx.HTTPError, Exception):
            return None

    # ── Shared helpers ────────────────────────────────────────────────

    @staticmethod
    def _extract_content(payload: dict) -> str | None:
        choices = payload.get("choices") or []
        if not choices:
            return None
        content = choices[0].get("message", {}).get("content")
        if content:
            return " ".join(str(content).split())
        return None


class AsyncStreamResult:
    """Wraps an httpx streaming response for SSE-like consumption."""

    def __init__(self, response: httpx.Response, source: str) -> None:
        self._response = response
        self.source = source

    async def __aenter__(self) -> "AsyncStreamResult":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._response.aclose()

    async def iter_text_chunks(self):
        """Yield text deltas as they arrive from the SSE stream."""
        full_text = ""
        async for line in self._response.aiter_lines():
            if not line.startswith("data: "):
                continue
            data_str = line[6:].strip()
            if data_str == "[DONE]":
                break
            try:
                data = json.loads(data_str)
                delta = (
                    data.get("choices", [{}])[0]
                    .get("delta", {})
                    .get("content", "")
                )
                if delta:
                    full_text += delta
                    yield delta
            except json.JSONDecodeError:
                continue

    async def collect_full(self) -> str:
        """Collect all chunks and return the full text."""
        parts = []
        async for chunk in self.iter_text_chunks():
            parts.append(chunk)
        return "".join(parts)


# Singleton
llm_client = LLMClient()