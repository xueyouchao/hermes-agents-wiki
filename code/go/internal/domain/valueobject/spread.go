package valueobject

type Spread struct {
    Bid       float64
    Ask       float64
    Midpoint  float64
    Percentage float64
}

func NewSpread(bid, ask float64) Spread {
    mid := (bid + ask) / 2
    return Spread{
        Bid:        bid,
        Ask:        ask,
        Midpoint:   mid,
        Percentage: (ask - bid) / mid * 100,
    }
}

func (s Spread) IsProfitable(minBps float64) bool {
    return s.Percentage*100 >= minBps
}
