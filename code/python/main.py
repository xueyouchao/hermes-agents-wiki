# python/main.py
import asyncio
import logging
import os
from internal.container import Container
from uvicorn import Config, Server
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

async def main():
    cfg = {
        "llm_provider": "openrouter",
        "llm_model": os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4"),
        "grpc_port": int(os.getenv("GRPC_PORT", "50051")),
    }
    container = Container(cfg)
    
    # Start gRPC
    await container.start()
    
    # Start FastAPI (health/API)
    config = Config(container.api, host="0.0.0.0", port=8000)
    server = Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
