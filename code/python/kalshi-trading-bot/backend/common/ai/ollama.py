"""Ollama AI client — unified analysis and classification using OpenAI-compatible API.

Primary model: glm-5.1:cloud (analysis, reasoning)
Fast model:  minimax-m2.7:cloud (classification, quick checks)

Both are accessed via Ollama's OpenAI-compatible /v1/chat/completions endpoint.
"""
import json
import logging
import time
from typing import Optional, Dict, Any

import httpx

from backend.common.config import settings
from .base import AIAnalysis, AnomalyReport, TradeRecommendation, AIProvider

logger = logging.getLogger("trading_bot.ai")


class OllamaClient:
    """Ollama AI client using OpenAI-compatible API.

    Works with any Ollama model, including cloud models like
    glm-5.1:cloud and minimax-m2.7:cloud that are served through
    an Ollama subscription.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        analysis_model: Optional[str] = None,
        classify_model: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.OLLAMA_API_KEY or ""
        self.analysis_model = analysis_model or settings.OLLAMA_ANALYSIS_MODEL
        self.classify_model = classify_model or settings.OLLAMA_CLASSIFY_MODEL
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Lazy-init httpx client for connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Content-Type": "application/json",
                    **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
                },
                timeout=120.0,  # cloud models can be slow
            )
        return self._client

    async def close(self):
        """Close the httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Call the Ollama OpenAI-compatible chat API.

        Returns the assistant's message content as a string.
        """
        client = await self._ensure_client()
        payload = {
            "model": model or self.analysis_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        start = time.time()
        try:
            resp = await client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            latency_ms = (time.time() - start) * 1000

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            logger.info(
                f"[Ollama/{model or self.analysis_model}] "
                f"{len(content)} chars, {latency_ms:.0f}ms, "
                f"tokens={usage.get('total_tokens', '?')}"
            )
            return content

        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code} {e.response.text[:500]}")
            raise
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise

    async def analyze_signal(
        self,
        signal_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AIAnalysis:
        """Analyze a trading signal using the primary (glm-5.1) model."""
        from .base import create_signal_prompt

        prompt = create_signal_prompt(signal_data, context)
        start = time.time()

        try:
            response = await self._chat(
                messages=[
                    {"role": "system", "content": "You are a quantitative trading analyst. Provide concise, actionable analysis of prediction market signals."},
                    {"role": "user", "content": prompt},
                ],
                model=self.analysis_model,
                temperature=0.3,
            )
            latency_ms = (time.time() - start) * 1000

            # Try to parse structured data from the response
            confidence = 0.5
            recommendation = None
            risk_factors = []

            # Simple parsing — model may return structured or free-form text
            lines = response.strip().split("\n")
            for line in lines:
                lower = line.lower().strip()
                if lower.startswith("confidence:") or lower.startswith("confidence "):
                    try:
                        val = float("".join(c for c in lower.split(":")[-1].strip() if c.isdigit() or c == "."))
                        confidence = min(max(val / 100 if val > 1 else val, 0), 1)
                    except (ValueError, IndexError):
                        pass
                elif lower.startswith("recommendation:") or lower.startswith("recommend "):
                    recommendation = line.split(":", 1)[-1].strip()
                elif "risk" in lower and ":" in lower:
                    risk_factors.append(line.split(":", 1)[-1].strip())

            return AIAnalysis(
                reasoning=response,
                confidence=confidence,
                recommendation=recommendation,
                risk_factors=risk_factors,
                raw_response=response,
                model_used=self.analysis_model,
                provider=AIProvider.OLLAMA.value,
                latency_ms=latency_ms,
                tokens_used=0,  # Ollama doesn't always return usage
            )

        except Exception as e:
            logger.error(f"Signal analysis failed: {e}")
            return AIAnalysis(
                reasoning=f"Analysis failed: {e}",
                confidence=0.0,
                model_used=self.analysis_model,
                provider=AIProvider.OLLAMA.value,
                latency_ms=(time.time() - start) * 1000,
            )

    async def classify_market(
        self,
        title: str,
        description: str = "",
    ) -> tuple[str, float]:
        """Classify a market using the fast (minimax-m2.7) model.

        Returns (category, confidence).
        """
        from .base import create_classification_prompt

        prompt = create_classification_prompt(title, description)

        try:
            response = await self._chat(
                messages=[
                    {"role": "system", "content": "You are a market classifier. Respond in the exact format: category,confidence"},
                    {"role": "user", "content": prompt},
                ],
                model=self.classify_model,
                temperature=0.1,
                max_tokens=50,
            )

            # Parse "category,confidence" format
            response = response.strip().lower()
            # Remove any extra text, keep only the category,confidence part
            lines = response.split("\n")
            last_line = lines[-1].strip()

            parts = last_line.split(",")
            category = parts[0].strip()
            confidence = 0.5
            if len(parts) > 1:
                try:
                    conf_val = float(parts[1].strip().rstrip("%"))
                    confidence = min(max(conf_val / 100 if conf_val > 1 else conf_val, 0), 1)
                except ValueError:
                    pass

            valid_categories = {"weather", "crypto", "politics", "economics", "sports", "other"}
            if category not in valid_categories:
                category = "other"
                confidence = 0.3

            return category, confidence

        except Exception as e:
            logger.warning(f"Market classification failed: {e}")
            return "other", 0.3

    async def detect_anomalies(
        self,
        markets: list[Dict[str, Any]],
    ) -> list[AnomalyReport]:
        """Detect anomalies in market data using the analysis model."""
        if not markets:
            return []

        prompt = f"""Analyze these {len(markets)} prediction markets for anomalies (price spikes, unusual volumes, spread anomalies).

Markets summary:
{json.dumps([{'ticker': m.get('ticker', '?'), 'yes_price': m.get('yes_price', 0), 'volume': m.get('volume', 0), 'spread': m.get('spread', 0)} for m in markets[:20]], indent=2)}

For each anomaly found, respond in JSON format:
[{{"ticker": "...", "type": "price_spike|volume_anomaly|spread_unusual", "severity": "low|medium|high", "description": "..."}}]

If no anomalies, respond with: []"""

        try:
            response = await self._chat(
                messages=[
                    {"role": "system", "content": "You are a market surveillance system. Detect anomalies in prediction market data. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            # Parse JSON response
            # Handle markdown code blocks
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            anomalies_data = json.loads(cleaned)
            reports = []
            for a in anomalies_data:
                reports.append(AnomalyReport(
                    market_ticker=a.get("ticker", "unknown"),
                    anomaly_type=a.get("type", "unknown"),
                    severity=a.get("severity", "low"),
                    description=a.get("description", ""),
                    ai_analysis=response,
                ))
            return reports

        except json.JSONDecodeError:
            logger.warning(f"Failed to parse anomaly JSON: {response[:200]}")
            return []
        except Exception as e:
            logger.warning(f"Anomaly detection failed: {e}")
            return []


# Module-level singleton
ollama_client: Optional[OllamaClient] = None


async def get_ollama_client() -> OllamaClient:
    """Get or create the shared Ollama client singleton."""
    global ollama_client
    if ollama_client is None:
        ollama_client = OllamaClient()
    return ollama_client


async def analyze_signal_with_ollama(signal_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIAnalysis:
    """Convenience wrapper — analyze a signal using Ollama."""
    client = await get_ollama_client()
    return await client.analyze_signal(signal_data, context)


async def classify_market_with_ollama(title: str, description: str = "") -> tuple[str, float]:
    """Convenience wrapper — classify a market using Ollama."""
    client = await get_ollama_client()
    return await client.classify_market(title, description)