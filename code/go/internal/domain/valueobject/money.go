package valueobject

type Currency string

const (
    USDC Currency = "USDC"
    ETH  Currency = "ETH"
    BTC  Currency = "BTC"
)

type Money struct {
    Amount   float64
    Currency Currency
}
