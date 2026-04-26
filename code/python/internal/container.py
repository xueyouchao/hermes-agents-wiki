# internal/container.py
from internal.llm.client import LLMClient
from internal.agents.arbitrage_agent import ArbitrageAgent
from internal.infrastructure.grpc_server import GrpcServer
from internal.api.main import create_app

class Container:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.llm = LLMClient(
            provider=cfg.get("llm_provider", "openrouter"),
            model=cfg.get("llm_model", "anthropic/claude-sonnet-4"),
        )
        self.agent = ArbitrageAgent(self.llm)
        self.grpc = GrpcServer(self.agent, port=cfg.get("grpc_port", 50051))
        self.api = create_app(self.agent)

    async def start(self):
        await self.grpc.start()

    async def stop(self):
        await self.llm.close()
        await self.grpc.stop()
