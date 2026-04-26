package aggregate

import (
    "time"
    "polymarket-arbitrage/internal/domain/event"
    "polymarket-arbitrage/internal/domain/valueobject"
)

type OpportunityState string

const (
    StateOpen      OpportunityState = "OPEN"
    StateExecuting OpportunityState = "EXECUTING"
    StateFilled    OpportunityState = "FILLED"
    StateExpired   OpportunityState = "EXPIRED"
    StateFailed    OpportunityState = "FAILED"
)

type Opportunity struct {
    ID         string
    MarketID   string
    Type       string
    State      OpportunityState
    Spread     valueobject.Spread
    Confidence float64
    TTL        time.Duration
    CreatedAt  time.Time
    ExpiresAt  time.Time
}

func NewOpportunity(id, marketID, oppType string, spread valueobject.Spread, conf float64, ttl time.Duration) *Opportunity {
    now := time.Now().UTC()
    return &Opportunity{
        ID:         id,
        MarketID:   marketID,
        Type:       oppType,
        State:      StateOpen,
        Spread:     spread,
        Confidence: conf,
        TTL:        ttl,
        CreatedAt:  now,
        ExpiresAt:  now.Add(ttl),
    }
}

func (o *Opportunity) Execute() {
    if o.State == StateOpen {
        o.State = StateExecuting
    }
}

func (o *Opportunity) Expire() {
    if o.State == StateOpen {
        o.State = StateExpired
    }
}

func (o *Opportunity) IsValid(now time.Time) bool {
    return o.State == StateOpen && now.Before(o.ExpiresAt)
}

func (o *Opportunity) IsProfitable(minBps float64) bool {
    return o.Spread.IsProfitable(minBps)
}

func (o *Opportunity) ToEvent() event.OpportunityDetected {
    return event.OpportunityDetected{
        OpportunityID: o.ID,
        MarketID:      o.MarketID,
        SpreadBps:     o.Spread.Percentage * 100,
        Confidence:    o.Confidence,
        DetectedAt:    o.CreatedAt,
    }
}
