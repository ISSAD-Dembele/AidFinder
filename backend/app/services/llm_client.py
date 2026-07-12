"""
LLM client for AidFinder.

Primary: OpenRouter (any model configured in .env)
Fallback: Qwen (DashScope)
If both are unavailable → returns None (caller uses conversation engine fallback)
"""

from __future__ import annotations

import json
import logging
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

logger = logging.getLogger("aidfinder.llm_client")


class LLMClient:
    """Unified LLM client: OpenRouter primary, Qwen fallback."""

    def __init__(self) -> None:
        self.openrouter_available = bool(OPENROUTER_API_KEY)
        self.qwen_available = bool(QWEN_API_KEY)
        logger.info(
            "[LLM INIT] OpenRouter disponible=%s | Qwen disponible=%s | "
            "OpenRouter URL=%s | Modèle=%s | Qwen URL=%s | Modèle=%s",
            self.openrouter_available,
            self.qwen_available,
            OPENROUTER_API_URL,
            OPENROUTER_MODEL,
            QWEN_API_URL,
            QWEN_MODEL,
        )

    @property
    def is_available(self) -> bool:
        available = self.openrouter_available or self.qwen_available
        if not available:
            logger.warning("[LLM] Aucun fournisseur LLM disponible (OpenRouter + Qwen absents)")
        return available

    # ── Sync generation (used by non-streaming paths & fallback) ──────

    def generate(self, messages: list[dict]) -> str | None:
        logger.info("[LLM generate] Appel synchrone LLM (nombre de messages=%d)", len(messages))

        logger.info("[LLM generate] Tentative OpenRouter en premier...")
        response = self._call_openrouter(messages)
        if response is not None:
            logger.info("[LLM generate] Succès OpenRouter — réponse obtenue")
            return response

        if self.openrouter_available:
            logger.warning("[LLM generate] OpenRouter a échoué, tentative fallback Qwen...")
        else:
            logger.warning("[LLM generate] OpenRouter non configuré, tentative Qwen...")

        response = self._call_qwen(messages)
        if response is not None:
            logger.info("[LLM generate] Succès Qwen — réponse obtenue")
            return response

        logger.error("[LLM generate] TOUS les fournisseurs LLM ont échoué — rend None")
        return None

    # ── Async streaming generation ────────────────────────────────────

    async def generate_stream(
        self, messages: list[dict]
    ) -> AsyncStreamResult | None:
        """Return an AsyncStreamResult or None if no provider available."""
        logger.info("[LLM stream] Appel asynchrone stream LLM (messages=%d)", len(messages))

        if self.openrouter_available:
            logger.info("[LLM stream] Tentative OpenRouter stream...")
            stream = await self._call_openrouter_stream(messages)
            if stream is not None:
                logger.info("[LLM stream] Succès OpenRouter stream")
                return stream
            logger.warning("[LLM stream] OpenRouter stream a échoué")

        if self.qwen_available:
            logger.info("[LLM stream] Tentative Qwen stream...")
            stream = await self._call_qwen_stream(messages)
            if stream is not None:
                logger.info("[LLM stream] Succès Qwen stream")
                return stream
            logger.warning("[LLM stream] Qwen stream a échoué")

        logger.error("[LLM stream] TOUS les fournisseurs stream ont échoué — rend None")
        return None

    # ── OpenRouter helpers ────────────────────────────────────────────

    def _call_openrouter(self, messages: list[dict]) -> str | None:
        if not self.openrouter_available:
            logger.warning("[OpenRouter sync] NON CONFIGURÉ (clé API absente)")
            return None

        # Log du prompt (sans la clé API)
        logger.info("[OpenRouter sync] URL=%s | Modèle=%s | Temperature=%s | MaxTokens=%s",
                     OPENROUTER_API_URL, OPENROUTER_MODEL,
                     OPENROUTER_TEMPERATURE, OPENROUTER_MAX_TOKENS)
        logger.info("[OpenRouter sync] Prompt envoyé (dernier message utilisateur) : %s",
                     messages[-1]["content"][:200] if messages else "(vide)")
        logger.debug("[OpenRouter sync] Messages complets : %s",
                      json.dumps(messages, default=str, ensure_ascii=False)[:1000])

        try:
            resp = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": "Bearer [API_KEY_CACHÉE]",
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

            logger.info("[OpenRouter sync] Code HTTP reçu : %d", resp.status_code)

            if resp.status_code != 200:
                logger.error("[OpenRouter sync] Erreur HTTP %d — Corps: %s",
                              resp.status_code, resp.text[:500])
                try:
                    resp.raise_for_status()
                except requests.RequestException:
                    return None

            payload = resp.json()
            content = self._extract_content(payload)
            if content:
                logger.info("[OpenRouter sync] Texte brut reçu (début) : %s...", content[:200])
            else:
                logger.warning("[OpenRouter sync] Réponse vide ou mal formée — payload=%s",
                                json.dumps(payload, default=str)[:300])

            return content

        except requests.ConnectionError as e:
            logger.error("[OpenRouter sync] ERREUR CONNEXION — %s", e)
            return None
        except requests.Timeout as e:
            logger.error("[OpenRouter sync] TIMEOUT (%ds) — %s", OPENROUTER_TIMEOUT_SECONDS, e)
            return None
        except requests.RequestException as e:
            logger.error("[OpenRouter sync] ERREUR REQUÊTE — %s", e)
            return None
        except json.JSONDecodeError as e:
            logger.error("[OpenRouter sync] ERREUR JSON — %s | Texte reçu: %s",
                          e, resp.text[:300] if 'resp' in dir() else "(inconnu)")
            return None
        except KeyError as e:
            logger.error("[OpenRouter sync] CLÉ MANQUANTE dans la réponse — %s", e)
            return None

    async def _call_openrouter_stream(self, messages: list[dict]) -> AsyncStreamResult | None:
        if not self.openrouter_available:
            logger.warning("[OpenRouter stream] NON CONFIGURÉ (clé API absente)")
            return None

        logger.info("[OpenRouter stream] URL=%s | Modèle=%s | Temperature=%s | MaxTokens=%s",
                     OPENROUTER_API_URL, OPENROUTER_MODEL,
                     OPENROUTER_TEMPERATURE, OPENROUTER_MAX_TOKENS)
        logger.info("[OpenRouter stream] Prompt (dernier message) : %s",
                     messages[-1]["content"][:200] if messages else "(vide)")

        try:
            async with httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    OPENROUTER_API_URL,
                    headers={
                        "Authorization": "Bearer [API_KEY_CACHÉE]",
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
                    logger.info("[OpenRouter stream] Code HTTP reçu : %d", response.status_code)

                    if response.status_code != 200:
                        body = await response.aread()
                        logger.error("[OpenRouter stream] Erreur HTTP %d — Corps: %s",
                                      response.status_code, body[:500].decode("utf-8", errors="replace"))
                        return None

                    return AsyncStreamResult(response=response, source="openrouter")

        except httpx.ConnectError as e:
            logger.error("[OpenRouter stream] ERREUR CONNEXION — %s", e)
            return None
        except httpx.TimeoutException as e:
            logger.error("[OpenRouter stream] TIMEOUT (%ds) — %s", OPENROUTER_TIMEOUT_SECONDS, e)
            return None
        except httpx.HTTPError as e:
            logger.error("[OpenRouter stream] ERREUR HTTPX — %s", e)
            return None
        except Exception as e:
            logger.error("[OpenRouter stream] ERREUR INATTENDUE — %s: %s", type(e).__name__, e)
            return None

    # ── Qwen helpers ──────────────────────────────────────────────────

    def _call_qwen(self, messages: list[dict]) -> str | None:
        if not self.qwen_available:
            logger.warning("[Qwen sync] NON CONFIGURÉ (clé API absente)")
            return None

        logger.info("[Qwen sync] URL=%s | Modèle=%s | Temperature=%s | MaxTokens=%s",
                     QWEN_API_URL, QWEN_MODEL, QWEN_TEMPERATURE, QWEN_MAX_TOKENS)
        logger.info("[Qwen sync] Prompt (dernier message) : %s",
                     messages[-1]["content"][:200] if messages else "(vide)")

        try:
            resp = requests.post(
                QWEN_API_URL,
                headers={
                    "Authorization": "Bearer [API_KEY_CACHÉE]",
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

            logger.info("[Qwen sync] Code HTTP reçu : %d", resp.status_code)

            if resp.status_code != 200:
                logger.error("[Qwen sync] Erreur HTTP %d — Corps: %s",
                              resp.status_code, resp.text[:500])
                try:
                    resp.raise_for_status()
                except requests.RequestException:
                    return None

            payload = resp.json()
            content = self._extract_content(payload)
            if content:
                logger.info("[Qwen sync] Texte brut reçu (début) : %s...", content[:200])
            else:
                logger.warning("[Qwen sync] Réponse vide ou mal formée — payload=%s",
                                json.dumps(payload, default=str)[:300])

            return content

        except requests.ConnectionError as e:
            logger.error("[Qwen sync] ERREUR CONNEXION — %s", e)
            return None
        except requests.Timeout as e:
            logger.error("[Qwen sync] TIMEOUT (%ds) — %s", QWEN_TIMEOUT_SECONDS, e)
            return None
        except requests.RequestException as e:
            logger.error("[Qwen sync] ERREUR REQUÊTE — %s", e)
            return None
        except json.JSONDecodeError as e:
            logger.error("[Qwen sync] ERREUR JSON — %s | Texte: %s",
                          e, resp.text[:300] if 'resp' in dir() else "(inconnu)")
            return None
        except KeyError as e:
            logger.error("[Qwen sync] CLÉ MANQUANTE — %s | Payload: %s",
                          e, json.dumps(payload, default=str)[:300] if 'payload' in dir() else "(inconnu)")
            return None

    async def _call_qwen_stream(self, messages: list[dict]) -> AsyncStreamResult | None:
        if not self.qwen_available:
            logger.warning("[Qwen stream] NON CONFIGURÉ (clé API absente)")
            return None

        logger.info("[Qwen stream] URL=%s | Modèle=%s | Temperature=%s | MaxTokens=%s",
                     QWEN_API_URL, QWEN_MODEL, QWEN_TEMPERATURE, QWEN_MAX_TOKENS)
        logger.info("[Qwen stream] Prompt (dernier message) : %s",
                     messages[-1]["content"][:200] if messages else "(vide)")

        try:
            async with httpx.AsyncClient(timeout=QWEN_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    QWEN_API_URL,
                    headers={
                        "Authorization": "Bearer [API_KEY_CACHÉE]",
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
                    logger.info("[Qwen stream] Code HTTP reçu : %d", response.status_code)

                    if response.status_code != 200:
                        body = await response.aread()
                        logger.error("[Qwen stream] Erreur HTTP %d — Corps: %s",
                                      response.status_code, body[:500].decode("utf-8", errors="replace"))
                        return None

                    return AsyncStreamResult(response=response, source="qwen")

        except httpx.ConnectError as e:
            logger.error("[Qwen stream] ERREUR CONNEXION — %s", e)
            return None
        except httpx.TimeoutException as e:
            logger.error("[Qwen stream] TIMEOUT (%ds) — %s", QWEN_TIMEOUT_SECONDS, e)
            return None
        except httpx.HTTPError as e:
            logger.error("[Qwen stream] ERREUR HTTPX — %s", e)
            return None
        except Exception as e:
            logger.error("[Qwen stream] ERREUR INATTENDUE — %s: %s", type(e).__name__, e)
            return None

    # ── Shared helpers ────────────────────────────────────────────────

    @staticmethod
    def _extract_content(payload: dict) -> str | None:
        choices = payload.get("choices") or []
        if not choices:
            logger.warning("[LLM extract] Aucun 'choices' dans la réponse")
            return None
        try:
            content = choices[0].get("message", {}).get("content")
            if content:
                return " ".join(str(content).split())
            logger.warning("[LLM extract] 'content' vide ou absent dans le choix 0")
            return None
        except (IndexError, KeyError, TypeError) as e:
            logger.error("[LLM extract] Erreur d'extraction — %s | Payload: %s",
                          e, json.dumps(payload, default=str)[:300])
            return None


class AsyncStreamResult:
    """Wraps an httpx streaming response for SSE-like consumption."""

    def __init__(self, response: httpx.Response, source: str) -> None:
        self._response = response
        self.source = source
        logger.debug("[AsyncStream] Initialisé source=%s", source)

    async def __aenter__(self) -> "AsyncStreamResult":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._response.aclose()
        logger.debug("[AsyncStream] Fermé")

    async def iter_text_chunks(self):
        """Yield text deltas as they arrive from the SSE stream."""
        full_text = ""
        chunk_count = 0
        async for line in self._response.aiter_lines():
            if not line.startswith("data: "):
                continue
            data_str = line[6:].strip()
            if data_str == "[DONE]":
                logger.debug("[AsyncStream] Signal [DONE] reçu — total chunks=%d", chunk_count)
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
                    chunk_count += 1
                    if chunk_count == 1:
                        logger.info("[AsyncStream] Premier chunk reçu: %s...", delta[:80])
                    yield delta
            except json.JSONDecodeError:
                logger.warning("[AsyncStream] Ligne SSE non JSON ignorée: %s", data_str[:100])
                continue

        if chunk_count > 0:
            logger.info("[AsyncStream] Stream terminé — %d chunks, %d caractères total",
                         chunk_count, len(full_text))
        else:
            logger.warning("[AsyncStream] Stream terminé — AUCUN chunk reçu")

    async def collect_full(self) -> str:
        """Collect all chunks and return the full text."""
        parts = []
        async for chunk in self.iter_text_chunks():
            parts.append(chunk)
        full = "".join(parts)
        logger.info("[AsyncStream] collect_full — %d caractères", len(full))
        return full


# Singleton
llm_client = LLMClient()