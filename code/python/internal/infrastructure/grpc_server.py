# internal/infrastructure/grpc_server.py
import asyncio
import logging
from concurrent import futures
import grpc
from google.protobuf import empty_pb2

from internal.agents.arbitrage_agent import ArbitrageAgent
from generated import signal_pb2, signal_pb2_grpc

class SignalService(signal_pb2_grpc.SignalServiceServicer):
    def __init__(self, agent: ArbitrageAgent):
        self.agent = agent

    async def GenerateSignal(self, request, context):
        signals = await self.agent.interpret(request.event_text)
        resp = signal_pb2.SignalResponse()
        for s in signals:
            resp.signals.add(
                contract_id=s.contract_id,
                direction=s.direction,
                confidence=s.confidence,
                action=s.action,
                ev_bps=s.ev_bps,
                reasoning=s.reasoning,
            )
        return resp

    async def StreamSignals(self, request_iterator, context):
        async for req in request_iterator:
            signals = await self.agent.interpret(req.event_text)
            for s in signals:
                yield signal_pb2.SignalResponse(signals=[
                    signal_pb2.Signal(
                        contract_id=s.contract_id,
                        direction=s.direction,
                        confidence=s.confidence,
                        action=s.action,
                        ev_bps=s.ev_bps,
                        reasoning=s.reasoning,
                    )
                ])

class GrpcServer:
    def __init__(self, agent: ArbitrageAgent, port: int = 50051):
        self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        self.port = port
        signal_pb2_grpc.add_SignalServiceServicer_to_server(SignalService(agent), self.server)
        self.server.add_insecure_port(f"[::]:{port}")

    async def start(self):
        await self.server.start()
        logging.info("gRPC server started on port %s", self.port)

    async def stop(self):
        await self.server.stop(5)
