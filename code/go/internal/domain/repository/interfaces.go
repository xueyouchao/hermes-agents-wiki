package repository

import (
    "context"
    "polymarket-arbitrage/internal/domain/aggregate"
)

type OpportunityRepository interface {
    Save(ctx context.Context, opp *aggregate.Opportunity) error
    FindByID(ctx context.Context, id string) (*aggregate.Opportunity, error)
    ListOpen(ctx context.Context, limit int) ([]*aggregate.Opportunity, error)
}

type TradeRepository interface {
    Save(ctx context.Context, trade *aggregate.Trade) error
    FindByID(ctx context.Context, id string) (*aggregate.Trade, error)
    ListByOpportunity(ctx context.Context, oppID string) ([]*aggregate.Trade, error)
}
