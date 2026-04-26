# Kalshi Trading Bot — Wiki Index

> Auto-generated index linking all GitNexus wiki pages.
> Codebase: 13 modules · 2,733 nodes · 3,961 edges · 64 communities

## Core

- [Trading Engine](trading-engine.md) — TradingEngine orchestrator, settlement logic, order lifecycle
- [Risk Management](risk-management.md) — 7 safety mechanisms — fee-adjusted edge, drawdown, exposure cap, auto-cancel
- [Configuration](configuration.md) — Settings, env vars, Ollama/Claude/Groq AI config
- [Database](database.md) — SQLAlchemy models, trade history, opportunity logging

## Use Cases

- [Weather Trading](weather-trading.md) — Weather arbitrage strategies A/B/C, scanner, signals, scheduler (7 files)
- [BTC Trading](btc-trading.md) — BTC 5-minute up/down strategy, signals, market fetchers (4 files)

## Infrastructure

- [AI Analysis](ai-analysis.md) — Ollama (glm-5.1:cloud / minimax-m2.7:cloud), Claude, Groq clients (5 files)
- [Exchange Integration](exchange-integration.md) — Kalshi exchange client, Polymarket abstraction layer (2 files)
- [Data Access](data-access.md) — Kalshi API client, market data fetching, retry logic (3 files)
- [API Layer](api-layer.md) — FastAPI dashboard backend, REST endpoints (1 file)
- [CLI Entry Points](cli-entry-points.md) — trade.py and run.py entry points, CLI flags
- [Frontend](frontend.md) — React/TypeScript dashboard, component architecture

## Additional

- [Other 04-26](other-04-26.md) — Gap analysis, review notes (Apr 26)
- [Other Docs](other-docs.md) — Documentation files, PlantUML diagrams
- [Other Python](other-python.md) — Python utility scripts and test infrastructure
- [Other Reviews](other-reviews.md) — Code review notes and findings

## Module → Source File Map

| Module | Source Files |
|--------|-------------|
| BTC Trading | btc_scheduler.py, signals.py, btc_markets.py, crypto.py |
| Weather Trading | weather_scheduler.py, weather_signals.py, weather.py, weather_markets.py, opportunity.py, opportunity_scanner.py, strategy_b.py |
| AI Analysis | base.py, claude.py, groq.py, ollama.py, logger.py |
| API Layer | main.py |
| Exchange Integration | base.py, kalshi.py |
| Data Access | kalshi_client.py, kalshi_markets.py, markets.py |
| Risk Management | risk.py |
| Trading Engine | trader.py, settlement.py |
| Database | database.py |
| Configuration | config.py |
| Frontend | App.tsx, api.ts, ... |