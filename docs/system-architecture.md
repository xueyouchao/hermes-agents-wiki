# Polymarket AI Arbitrage — System Architecture

## Overview

Hybrid architecture: Go handles data ingestion, execution, and temporal orchestration (performance-critical path). Python hosts LLM signal generation and LangChain agents (AI/reasoning path).

## Architecture Diagram

```
                    +---------------+
     (B2C Web/App)  |   API GW      |
     (Trading UI)    |  (Go + Echo)  |
                    +-------+-------+
                            |
        +-------------------+-------------------+
        |                                       |
+-------v-------+                  +-------------v----------+
|   Go Engine   |                  |   Python AI Bridge     |
| (Core)        |                  |   (Signal/LLM)         |
|               |                  |                        |
| +-----------+ | gRPC/stream      | +------------------+   |
| | Temporal  | |<---------------->| | LangChain Agent  |   |
| |  Server   | |                  | | (Reasoning Gap)  |   |
| +-----------+ |                  | +------------------+   |
|               |                  |                        |
| +-----------+ | REST/WebSocket   | +------------------+   |
| | Polymarket| |<------+          | | OpenRouter/      |   |
| |  Client   | |       |          | | Anthropic API    |   |
| +-----------+ |       |          | +------------------+   |
|               |       |          |                        |
| +-----------+ |       |          | +------------------+   |
| |  Binance  | |<------+          | | FRED/Fed News    |   |
| |  Client   | |       |          | | Scraper          |   |
| +-----------+ |       |          | +------------------+   |
|               |       |          |                        |
| +-----------+ |       |          | +------------------+   |
| |  Executor | |-------+          | | Fine-tuned Model |   |
| |  Engine   | |  (fill events)   | | (Signal Ranking) |   |
| +-----------+ |                  | +------------------+   |
|               |                  +-------------^----------+
| +-----------+ |                                |
| | Risk En-  | |<-------------------------------+
| |   gine    | |  (position limits, drawdown)     |
| +-----------+ |
|               |
| +-----------+ |
| |  Postgres | |
| |  (Events) | |
| +-----------+ |
|               |
| +-----------+ |
| |  Redis    | |
| |  (State)  | |
| +-----------+ |
+---------------+

+---------------+
|  Obs. Stack   |
| Prometheus +  |
| Grafana +     |
| Jaeger        |
+---------------+
```

## Component Breakdown

### Go Engine (Core Execution Path)

| Layer | Package | Responsibility |
|-------|---------|----------------|
| Interfaces | `interfaces/http` | REST handlers for webhooks, SignalR for real-time P&L |
| Application | `application/command` | RegisterOpportunity, ExecuteTrade, SettleTrade |
|             | `application/query` | GetOpenOpportunities, GetPnL |
| Domain | `domain/aggregate` | Opportunity, Trade, Signal (invariants) |
|        | `domain/event` | Domain events (OpportunityDetected, TradeLegExecuted) |
|        | `domain/valueobject` | Spread, Money, ConfidenceScore |
|        | `domain/service` | OpportunityScreener, ExecutionRouter, RiskManager |
|        | `domain/repository` | Port interfaces (no impl) |
| Infrastructure | `infrastructure/polymarket` | Polymarket REST/WS client + rate limiter |
|                | `infrastructure/binance` | Binance API client |
|                | `infrastructure/temporal` | Temporal worker registration, activity/impl |
|                | `infrastructure/db` | Postgres repository impl, Redis state |
|                | `infrastructure/llmclient` | gRPC client to Python AI Bridge |
| Config | `pkg/config` | Viper-based config (env + yaml) |
| Logger | `pkg/logger` | Zerostructured JSON logger |

### Python AI Bridge (Signal Generation Path)

| Module | File | Responsibility |
|--------|------|----------------|
| `agents` | `arbitrage_agent.py` | LangChain agent that detects reasoning/fragmentation gaps |
| `strategies` | `signal_ranker.py` | ML model (XGBoost/LightGBM) ranking signal quality |
| `llm` | `client.py` | OpenRouter/Anthropic API proxy with retry/circuit breaker |
| `infrastructure` | `grpc_server.py` | gRPC server serving SignalGeneration service |
| `api` | `main.py` | FastAPI app for health checks, metrics |

## Technology Stack

| Concern | Technology | Rationale |
|---------|------------|-----------|
| Language (core) | Go 1.22 | Goroutines for sub-ms concurrency; GC optimized for low-latency |
| Language (AI) | Python 3.11 | LangChain ecosystem; model inference libraries |
| Workflow Engine | Temporal | Durable execution for trade settlement; saga for cross-venue execution |
| Transport (core) | gRPC | Binary, streaming, schema-first |
| Transport (ext) | REST/WS | Polymarket/Binance APIs only expose these |
| DB (events) | Postgres 16 | WAL for event sourcing compatibility; JSONB for signal blobs |
| DB (state) | Redis 7 | Sub-millisecond read/write for position state and rate limiters |
| Observability | Prometheus + Grafana + Jaeger | Industry standard; Go SDK is excellent |
| DI Framework | Google Wire (Go) | Compile-time DI; zero runtime overhead |
| DI Framework | manual container (Python) | Simple enough; no runtime magic needed |

## Data Flow: Speed Gap Arbitrage

```
Polymarket WS --> Go Price Consumer --> Normalized Book (domain object)
                           |
                           v
Binance WS ---> Go Price Consumer ---->
                           |
                           v
                    Spread Calculator
                    (opportunity value object)
                           |
                           v
                    Temporal Workflow (StartOpportunityExecution)
                           |
              +------------+------------+
              |                         |
              v                         v
      RiskManager.Check()      ExecutionRouter.BestVenue()
              |                         |
              v                         v
      Pass --> TradeExecutor         Send orders (2 legs)
      Fail --> Reject                |
                             TradeLegExecuted events
                                     |
                                     v
                             Temporal Workflow (Saga)
                             - If leg 1 fills, must fill leg 2
                             - If leg 2 fails, reverse leg 1
                                     |
                                     v
                             OrderSettledEvent >> Postgres
```

## Data Flow: Reasoning Gap Arbitrage

```
Feed scraper (Fed, X, News) >> Python FastAPI endpoint
                                     |
                                     v
                          LLM Signal Interpreter (LangChain agent)
                                     |
                                     v
                          Signal aggregate (structured + confidence)
                                     |
                                     v
                          gRPC stream to Go Engine
                                     |
                                     v
                          OpportunityScreener (EV > threshold?)
                                     |
                                     v
                          Temporal Workflow (same execution pipeline)
```

## Key Configuration

```yaml
arbitrage:
  strategy: speed_gap             # or reasoning_gap, fragmentation_gap
  min_spread_bps: 5               # 0.05%
  max_position_usd: 10000
  max_drawdown_pct: 5
  opportunity_ttl_ms: 2500        # Target ≤ 2.7s per article
  
temporal:
  host: localhost:7233
  namespace: polymarket-arbitrage
  task_queue: arbitrage-main

polymarket:
  api_base: https://api.polymarket.com
  ws_endpoint: wss://ws.polymarket.com
  rate_limit: 100  # per second

binance:
  api_base: https://api.binance.com
  ws_endpoint: wss://stream.binance.com:9443/ws

llm:
  provider: ollama                  # Ollama Pro (cloud) or local on GPU box
  model: kimi-k2.6:cloud                  # Pulled via `ollama pull kimi-k2.6` on Pro account
  base_url: ${OLLAMA_HOST}          # https://ollama-pro.cloud/... or http://localhost:11434
  api_key: ${OLLAMA_API_KEY}        # Only required for Ollama Pro cloud inference
  temperature: 0.1                  # Deterministic; low variance for arbitrage signals
  num_ctx: 8192                     # Context window
  timeout_seconds: 8.0              # Must stay inside 2.7s execution window
```
