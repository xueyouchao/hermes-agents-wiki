# internal/agents/arbitrage_agent.py
"""Arbitrage reasoning agent backed by Ollama (Pro cloud or local)."""
import json
import logging
from dataclasses import dataclass
from typing import List

from internal.llm.client import LLMClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert prediction-market arbitrage analyst.
Given a raw news event or primary source, produce a structured arbitrage signal.

Rules:
1. Identify affected Polymarket contracts by their implied topic.
2. Direction: bullish / bearish / neutral.
3. Confidence: 0.0 to 1.0 (calibrated; 0.95+ only when source is primary).
4. Action: BUY_YES | BUY_NO | HOLD.
5. EV estimate in basis points of edge after fees.
6. Keep reasoning under 120 words.

Respond ONLY as valid JSON with exact keys:
  affected_contracts (list of strings),
  direction (string),
  confidence (float),
  action (string),
  ev_bps (float),
  reasoning (string)
"""

@dataclass(frozen=True)
class Signal:
    contract_id: str
    direction: str
    confidence: float
    action: str
    ev_bps: float
    reasoning: str
    raw_event: str

class ArbitrageAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def interpret(self, event_text: str) -> List[Signal]:
        try:
            raw = await self.llm.generate(SYSTEM_PROMPT, event_text, temperature=0.1)
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            return []

        signals: List[Signal] = []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Sometimes models wrap JSON in markdown fences; strip them
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                cleaned = "\n".join(lines[1:-1])  # remove fences
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                logger.warning("Unparseable LLM output: %s", raw[:200])
                return []

        for contract in parsed.get("affected_contracts", []):
            signals.append(Signal(
                contract_id=contract,
                direction=parsed.get("direction", "neutral"),
                confidence=parsed.get("confidence", 0.0),
                action=parsed.get("action", "HOLD"),
                ev_bps=parsed.get("ev_bps", 0.0),
                reasoning=parsed.get("reasoning", ""),
                raw_event=event_text,
            ))
        return signals
