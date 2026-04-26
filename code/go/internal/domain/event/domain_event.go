package event

type DomainEvent interface {
    EventName() string
    OccurredAt() time.Time
}

type OpportunityDetected struct {
    OpportunityID string
    MarketID      string
    SpreadBps     float64
    Confidence    float64
    DetectedAt    time.Time
}

func (e OpportunityDetected) EventName() string  { return "OpportunityDetected" }
func (e OpportunityDetected) OccurredAt() time.Time { return e.DetectedAt }
