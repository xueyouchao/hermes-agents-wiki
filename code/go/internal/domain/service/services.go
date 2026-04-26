package service

import (
    "context"
    "time"
    "polymarket-arbitrage/internal/domain/aggregate"
    "polymarket-arbitrage/internal/domain/valueobject"
)

type VenueQuote struct {
    Venue string
    Bid   float64
    Ask   float64
}

type OpportunityScreener struct {
    minSpreadBps float64
}

func NewOpportunityScreener(minBps float64) *OpportunityScreener {
    return &OpportunityScreener{minSpreadBps: minBps}
}

func (s *OpportunityScreener) Screen(ctx context.Context, marketID string, quotes []VenueQuote) (*aggregate.Opportunity, error) {
    // Simplified: find best bid vs best ask across venues
    var bestBid, bestAsk *VenueQuote
    for _, q := range quotes {
        if bestBid == nil || q.Bid > bestBid.Bid {
            bestBid = &q
        }
        if bestAsk == nil || q.Ask < bestAsk.Ask {
            bestAsk = &q
        }
    }
    if bestBid == nil || bestAsk == nil || bestBid.Venue == bestAsk.Venue {
        return nil, nil
    }
    spread := valueobject.NewSpread(bestBid.Bid, bestAsk.Ask)
    if !spread.IsProfitable(s.minSpreadBps) {
        return nil, nil
    }
    opp := aggregate.NewOpportunity(
        uuid.New().String(),
        marketID,
        "speed_gap",
        spread,
        1.0,
        2700*time.Millisecond,
    )
    return opp, nil
}

type ExecutionRouter struct{}

func NewExecutionRouter() *ExecutionRouter { return &ExecutionRouter{} }

func (r *ExecutionRouter) Route(ctx context.Context, opp *aggregate.Opportunity) ([]aggregate.Leg, error) {
    legs := make([]aggregate.Leg, 0, 2)
    // Simplified: route half buy/sell across the spread
    legs = append(legs, aggregate.Leg{Venue: "polymarket", Side: "BUY", Amount: 100})
    legs = append(legs, aggregate.Leg{Venue: "binance", Side: "SELL", Amount: 100})
    return legs, nil
}

type RiskManager struct {
    maxPositionUSD float64
    currentExposure float64
}

func NewRiskManager(maxUSD float64) *RiskManager {
    return &RiskManager{maxPositionUSD: maxUSD}
}

func (r *RiskManager) Evaluate(ctx context.Context, opp *aggregate.Opportunity, legs []aggregate.Leg) error {
    total := 0.0
    for _, l := range legs {
        total += l.Amount
    }
    if r.currentExposure+total > r.maxPositionUSD {
        return errors.New("risk limit exceeded")
    }
    return nil
}
