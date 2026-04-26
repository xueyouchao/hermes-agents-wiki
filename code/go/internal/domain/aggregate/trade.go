package aggregate

import (
    "time"
    "polymarket-arbitrage/internal/domain/valueobject"
)

type TradeState string

const (
    TradePending   TradeState = "PENDING"
    TradeExecuted  TradeState = "EXECUTED"
    TradeSettled   TradeState = "SETTLED"
    TradeFailed    TradeState = "FAILED"
)

type Leg struct {
    Venue      string
    Side       string
    Amount     float64
    Price      float64
    FilledAt   *time.Time
    ExternalID string
}

type Trade struct {
    ID            string
    OpportunityID string
    Legs          []Leg
    State         TradeState
    PnL           *valueobject.Money
    Commission    *valueobject.Money
    CreatedAt     time.Time
    SettledAt     *time.Time
}
