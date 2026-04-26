//+build wireinject

package main

import (
    "github.com/google/wire"
    "polymarket-arbitrage/internal/application/workflow"
    "polymarket-arbitrage/internal/domain/repository"
    "polymarket-arbitrage/internal/domain/service"
    "polymarket-arbitrage/internal/infrastructure/binance"
    "polymarket-arbitrage/internal/infrastructure/db"
    "polymarket-arbitrage/internal/infrastructure/polymarket"
    "polymarket-arbitrage/internal/infrastructure/temporal"
    "polymarket-arbitrage/pkg/config"
    "polymarket-arbitrage/pkg/logger"
)

// Provider for config (one-time load)
func ProvideConfig() *config.Config {
    return config.Load()
}

// Provider for logging
func ProvideLogger(cfg *config.Config) (*logger.Logger, error) {
    return logger.New(cfg.LogLevel), nil
}

// Repository providers
func ProvideOpportunityRepository(cfg *config.Config) (repository.OpportunityRepository, error) {
    return db.NewPostgresOpportunityRepo(cfg.PostgresDSN)
}

func ProvideTradeRepository(cfg *config.Config) (repository.TradeRepository, error) {
    return db.NewPostgresTradeRepo(cfg.PostgresDSN)
}

// Domain service providers
func ProvideOpportunityScreener(cfg *config.Config) *service.OpportunityScreener {
    return service.NewOpportunityScreener(cfg.MinSpreadBps)
}

func ProvideExecutionRouter() *service.ExecutionRouter {
    return service.NewExecutionRouter()
}

func ProvideRiskManager(cfg *config.Config) *service.RiskManager {
    return service.NewRiskManager(cfg.MaxPositionUSD)
}

// Infrastructure providers
func ProvidePolymarketClient(cfg *config.Config) *polymarket.Client {
    return polymarket.NewClient(cfg.PolymarketAPI, cfg.PolymarketWS)
}

func ProvideBinanceClient(cfg *config.Config) *binance.Client {
    return binance.NewClient(cfg.BinanceAPI, cfg.BinanceWS)
}

// Temporal providers
func ProvideTemporalClient(cfg *config.Config) (*temporal.Client, error) {
    return temporal.NewClient(cfg.TemporalHost)
}

func ProvideTemporalWorker(
    client *temporal.Client,
    activities *workflow.ActivitiesImpl,
) *temporal.Worker {
    return temporal.NewWorker(client, activities)
}

// Activity implementation (combines all dependencies)
func ProvideActivities(
    oppRepo repository.OpportunityRepository,
    tradeRepo repository.TradeRepository,
    router *service.ExecutionRouter,
    risk *service.RiskManager,
    polyClient *polymarket.Client,
    binClient *binance.Client,
) *workflow.ActivitiesImpl {
    return &workflow.ActivitiesImpl{
        OppRepo:       oppRepo,
        TradeRepo:     tradeRepo,
        Router:        router,
        RiskMgr:       risk,
        Polymarket:    polyClient,
        Binance:       binClient,
    }
}

// Application container
var AppSet = wire.NewSet(
    ProvideConfig,
    ProvideLogger,
    ProvideOpportunityRepository,
    ProvideTradeRepository,
    ProvideOpportunityScreener,
    ProvideExecutionRouter,
    ProvideRiskManager,
    ProvidePolymarketClient,
    ProvideBinanceClient,
    ProvideTemporalClient,
    ProvideActivities,
    ProvideTemporalWorker,
    // bind interface to impl
    wire.Bind(new(workflow.OpportunityActivities), new(*workflow.ActivitiesImpl)),
)

// Build container
func BuildApp() (*App, error) {
    wire.Build(
        AppSet,
        NewApp,
    )
    return nil, nil
}
