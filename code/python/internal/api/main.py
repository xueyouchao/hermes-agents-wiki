# internal/api/main.py
import logging
from fastapi import FastAPI
from internal.agents.arbitrage_agent import ArbitrageAgent

def create_app(agent: ArbitrageAgent) -> FastAPI:
    app = FastAPI(title="Polymarket AI Signal Bridge", version="0.1.0")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/signal")
    async def signal(body: dict):
        text = body.get("event_text", "")
        signals = await agent.interpret(text)
        return {"signals": [s.__dict__ for s in signals]}

    @app.get("/metrics")
    async def metrics():
        return {"latency_ms": 120, "requests_per_min": 45}
    
    return app
