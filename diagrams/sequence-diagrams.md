# Sequence Diagrams — Polymarket AI Arbitrage System

## Diagram 1: Speed Gap Arbitrage (Primary Flow)

```
Polymarket                 Go Engine                  Binance               Temporal              Risk Mgr            Executor
     |                         |                         |                     |                    |                  |
     | WS tick                 |                         |                     |                    |                  |
     |-------------------------|                         |                     |                    |                  |
     |                         |  (normalized book)      |                     |                    |                  |
     |                         |                         | WS tick             |                    |                  |
     |                         |                         |-----------------------                    |                  |
     |                         |                         |                     |                    |                  |
     |                         |  (compare books)      |                     |                    |                  |
     |                         |  Spread VO created    |                     |                    |                  |
     |                         |  spread=12bps         |                     |                    |                  |
     |                         |  ----------\            |                     |                    |                  |
     |                         |            \            |                     |                    |                  |
     |                         |             v            |                     |                    |                  |
     |                         |  OpportunityAggregate    |                     |                    |                  |
     |                         |  (state=OPEN, TTL=2.5s) |                     |                    |                  |
     |                         |  ----------|---------->  |                     |                    |                  |
     |                         |                         |                     |                    |                  |
     |                         |            |            |                     |                    |                  |
     |                         |            v            |                     |                    |                  |
     |                         |  StartWorkflow(OpportunityExecutionWF)        |                    |                  |
     |                         |  --------------------------------------------|                    |                  |
     |                         |            |            |                     |                    |                  |
     |                         |            |            |                     |  Check position     |                  |
     |                         |            |            |                     |  & drawdown       |                  |
     |                         |            |            |                     | <-----------------<                   |
     |                         |            |            |                     |                     |                  |
     |                         |            |            |                     |  PASS / FAIL      |                  |
     |                         |            |            |                     | >----------------->                   |
     |                         |            |            |                     |                     |                  |
     |                         |            v            |                     |                     |                  |
     |                         |  Activity: RouteExecution()                  |                     |                  |
     |                         |  (latency-weighted venue selection)            |                     |                  |
     |                         |            |            |                     |                     |                  |
     |                         |            v            |                     |                     |                  |
     |                         |  [Par] Leg 1: Buy(Polymarket)\              |                     |                  |
     |-------------------------------------------------------------------------|                     |                  |
     |                         |            |                                |                     |                  |
     |                         |            |  [Par] Leg 2: Sell(Binance)     |                     |                  |
     |                         |            |-------------------------------------------|           |                  |
     |                         |            |                                |                     |                  |
     |                         |            |  fill_confirmations back       |                     |                  |
     |                         |            |<------------------------------------------------------------------|                  |
     |                         |            |                                |                     |                  |
     |                         |            v                                |                     |                  |
     |                         |  TradeAggregate (state=EXECUTED)              |                     |                  |
     |                         |  PnL = +$89 USD                             |                     |                  |
     |                         |            |                                |                     |                  |
     |                         |  Event: TradeSettled >> Postgres             |                     |                  |
     |                         |            |                                |                     |                  |
```

## Diagram 2: Reasoning Gap Arbitrage (LLM Signal Flow)

```
News Feed          Python Bridge           LLM Agent          Go Engine          Temporal      Executor
   |                     |                     |                    |                 |             |
   | raw_text            |                     |                    |                 |             |
   |-------------------->|                     |                    |                 |             |
   |                     |  prompt             |                    |                 |             |
   |                     |-------------------->|                    |                 |             |
   |                     |                     |                    |                 |             |
   |                     |                     | Anthropic/OpenRouter                |             |
   |                     |                     |--------------------                |             |
   |                     |                     |<--------------------                 |             |
   |                     |                     |                    |                 |             |
   |                     |  structured_signal  |                    |                 |             |
   |                     | (Signal aggregate)  |                    |                 |             |
   |                     |  confidence=0.87    |                    |                 |             |
   |                     |---------------------                    |                 |             |
   |                     |                     |                    |                 |             |
   |  gRPC stream        |                     |                    |                 |             |
   |  (broadcast)        |                     |                    |                 |             |
   |  -----------------  |  -----------------  |  >>>>>>>>>>    |                 |             |
   |                     |                     |                    |  OpportunityScreener           |
   |                     |                     |                    |  (EV = 15bps > 5bps min?)      |
   |                     |                     |                    |                 |             |
   |                     |                     |                    |  YES ---> StartWorkflow(ReasoningGapWF)
   |                     |                     |                    |          |        |             |
   |                     |                     |                    |          |        |             |
   |                     |                     |                    |          |        v             v
   |                     |                     |                    |          |   (same exec pipeline as speed gap)
```

## Diagram 3: Temporal SAGA — Compensation on Failure

```
Trader Workflow (Temporal)
     |
     v
[Activity 1] PlaceBuyLeg(Polymarket)
     |         \  success                    failure
     |          \                           |
     |           v                           v
     |    [Activity 2] PlaceSellLeg(Binance) [Compensation] ReverseBuyLeg(Polymarket)
     |         \  success                    failure
     |          \                           |
     |           v                           v
     |    [Activity 3] ConfirmSettlement   [Compensation] ReverseSellLeg(Binance)
     |     (poll until on-chain confirm)
     |         \  success                    timeout
     |          \                           |
     |           v                           v
     |    Transaction COMPLETE            [Compensation] ReverseBuyLeg + ReverseSellLeg
     |                                     + Alert RiskManager
```

Saga Logic (Temporal Go SDK):

  ctx := workflow.WithActivityOptions(ctx, ao)
  
  err := workflow.ExecuteActivity(ctx, PlaceBuyLeg, leg1).Get(ctx, &buyResult)
  if err != nil {
     return err  // nothing to compensate yet
  }
  
  // register compensation
defer func() {
     if err != nil {
        _ = workflow.ExecuteActivity(ctx, ReverseBuyLeg, buyResult).Get(ctx, nil)
     }
  }()
  
  err = workflow.ExecuteActivity(ctx, PlaceSellLeg, leg2).Get(ctx, &sellResult)
  if err != nil {
     return err  // triggers compensation above
  }
  
  defer func() {
     if err != nil {
        _ = workflow.ExecuteActivity(ctx, ReverseSellLeg, sellResult).Get(ctx, nil)
     }
  }()
  
  err = workflow.ExecuteActivity(ctx, ConfirmSettlement, trade).Get(ctx, nil)
```

## Diagram 4: Dependency Injection Wiring

```
main.go
  |
  v
ProvideLogger() ------>  Wire(App)
ProvideConfig() ------>   (compile-time DI)
ProvidePostgres() --->
ProvideRedis() ------>
ProvideTemporal() --->
ProvidePolymarketClient()    
ProvideBinanceClient()     
ProvideRiskManager()    
ProvideExecutionRouter()    
v
+----------------------+
|   polymarket-arbitrage |
|   (wire_gen.go       |
|    generated)        |
+----------------------+
| startup sequence:    |
| 1. init DB/Redis     |
| 2. register Temporal |
|    workers           |
| 3. start gRPC client |
|    to Python bridge  |
| 4. subscribe WS feeds|
| 5. start HTTP server |
+----------------------+
```

Python Bridge (manual container):

  main.py
  |
  v
  Container()
  |
  +--> LLMClient(cfg)
  +--> SignalInterpreter(llm_client)
  +--> GrpcServer(signal_interpreter)
  +--> FastAPI(fastapi_app)
  |
  v
  asyncio.run(start_all())

## Diagram 5: Rolling Disruption — Model Update Loop

```
Anthropic Release       System Maintainer          Python Bridge         Signal Quality DB
        |                       |                        |                      |
        v                       |                        |                      |
   "Claude Mythos" leaked       |                        |                      |
  (market perturbation)         |   detects new model    |                      |
        |                       |   in changelog/news    |                      |
        |                       |----------------------->|                      |
        |                       |                        |                      |
        |                       |   update model config  |                      |
        |                       |   (A/B switch)         |                      |
        |                       |----------------------->|                      |
        |                       |                        |                      |
        |                       |   Signal quality test    (backtest 1hr)       |
        |                       |                        |                      |
        |                       |   <------------------->  (query Signal DB)    |
        |                       |   quality > prior?                             |
        |                       |                        |                      |
        |                       |   YES -->  activate new model                  |
        |                       |                        |                      |
        |                       |   (arbitrage window captured)                   |
        |                       |                        |                      |
```
