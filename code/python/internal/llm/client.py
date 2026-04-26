# internal/llm/client.py
import os
from typing import Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Ollama-native client. Works for:
      - Ollama Pro cloud inference (what you purchased)
      - Ollama local server on WSL/GPU box
    
    Endpoint must expose Ollama HTTP API (default port 11434 for local;
    Ollama Pro gives you a cloud endpoint URL).
    """
    def __init__(
        self,
        base_url: Optional[str] = None,      # e.g. "https://ollama-pro.example.com" or "http://localhost:11434"
        model: Optional[str] = None,         # e.g. "kimi-k2.6:cloud", "qwen2.5:32b", "llama3.3:70b"
        timeout_seconds: float = 8.0,        # tight for arbitrage 2.7s window
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "kimi-k2.6:cloud")
        self.timeout = timeout_seconds
        
        headers = {"Content-Type": "application/json"}
        # Ollama Pro cloud inference often uses bearer token auth
        token = os.getenv("OLLAMA_API_KEY")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout_seconds,
        )
        logger.info("LLMClient initialized | model=%s endpoint=%s", self.model, self.base_url)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,            # very low for deterministic reasoning
        num_ctx: int = 8192,                  # context window size
    ) -> str:
        """
        Returns raw text from the model. Caller must parse JSON if structured output required.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx,
                # deterministic sampling for arbitrage consistency
                "seed": 42,
            },
        }
        resp = await self.client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        # Ollama /api/chat returns: {"message": {"role": "assistant", "content": "..."}, ...}
        content = data.get("message", {}).get("content", "")
        logger.debug("LLM response | model=%s len=%d", self.model, len(content))
        return content

    async def close(self):
        await self.client.aclose()
