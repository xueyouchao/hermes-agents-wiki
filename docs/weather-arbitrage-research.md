# Polymarket Weather Arbitrage — Deep Research & Bot Implementation Plan

## 1. Source Article Analysis

Kirill (@kirillk_web3) published "How to Build a Polymarket Weather Bot with Kimi Claw — $100K/Month" on April 14, 2026.

Key data points from the article:
- Wallet 0x594edb... made $94,233 all-time profit on temperature brackets alone
- Joined Nov 2025, 4,776 predictions, biggest win $25.41 → $12,400
- $100K/month requires $15-30K capital across 15-25 daily entries in 8-10 cities
- Two core strategies: (A) ColdMath ultra-low bracket, (B) Spread Arbitrage

## 2. Polymarket Weather Markets — Live Snapshot (Apr 26, 2026)

211 total weather markets. Categories:

| Category    | Count | Typical Volume     |
|-------------|-------|--------------------|
| Temperature | ~180  | $10K-$46K per city |
| Precipitation| 4    | $16K-$68K monthly  |
| Global      | 7     | $33K-$3M          |
| Hurricanes  | 4     | $16K-$337K        |
| Earthquakes | 11    | $1M-$2M           |
| Volcanoes   | 2     | $75K-$1M          |
| Pandemics   | 8     | varies            |

### Cities with Daily Temperature Markets (highest volume)

Seoul, Mexico City, London, Shanghai, Austin, Hong Kong, Tokyo, Chicago,
Taipei, Munich, Chengdu, NYC, Ankara, Dallas, Wellington, Sao Paulo,
Singapore, Milan, Miami, Paris, Shenzhen, Buenos Aires, Kuala Lumpur,
Wuhan, Beijing, Atlanta, Jakarta, Houston, LA, Lucknow, Denver, Amsterdam,
Seattle, Madrid, Toronto, Chongqing, Panama City, Warsaw, Moscow,
San Francisco, Guangzhou, Karachi, Tel Aviv, Istanbul, Manila, Lagos,
Helsinki, Busan, Jeddah, Cape Town

### Market Structure

Each city has multiple temperature brackets for the SAME day:
- Example: "Highest temperature in Seoul on April 27?"
  - 18°C = 31% Yes    (most likely)
  - 19°C = 20% Yes    (less likely)
- Example: "Highest temperature in Dallas on April 27?"
  - 88°F or higher = 93% Yes  (near-certain)
  - 86-87°F = 4% Yes          (ultra-low probability)

Markets are BINARY (Yes/No) and resolve to $1.00 or $0.00.
YES price + NO price should = $1.00, but in thin markets they often DON'T.

## 3. Account Analysis — The Winners

### @hondacivic (HondaCivic)
- All-time P/L: +$56,344.04
- Predictions: 4,036
- Biggest win: $15,100
- Positions value: $1,998.98
- Active positions: Sao Paulo temp, Istanbul temp, F1 markets
- Profile: https://x.com/0xMarchyel

### @automatedaitradingbot
- All-time P/L: +$83,106.03
- Predictions: 2,903
- Biggest win: $30,400
- Positions value: $39.54
- Bio: "Meteorologist. IT engineer. Automated bot testing"
- Mix: weather + earthquakes + CS2 + cricket toss + SpaceX + UFC + culture

### ColdMath wallet (0x594edb...)
- All-time P/L: +$94,233
- Predictions: 4,776
- Strategy: Pure temperature brackets
- This is the archetype wallet from Kirill's article

## 4. Two Core Strategies — How They Actually Work

### Strategy A: ColdMath Ultra-Low Bracket (The Home Run Strategy)

**Concept**: Buy YES on temperature brackets priced at 0.1¢-2¢ that your
weather model says should be priced much higher.

**Example**:
- Market: "Will Dallas hit 88°F or higher on April 27?"
- Market price: YES = 93¢ (everyone agrees it's hot)
- BUT: "Will Dallas hit 94°F or higher?" might be priced at YES = 1¢
- Your weather model says there's a 15% chance of 94°F+
- You buy 1¢ YES shares for $10 = 1,000 shares
- If it hits (1 in ~7 tries): 1,000 × $1.00 = $1,000 (100x return)
- If it misses: you lose $10
- You need ~5% hit rate to be profitable at 0.1¢-2¢ entries

**The Math**:
- At 0.1¢ per share: 1 hit in 1,000 covers 999 misses
- At 1¢ per share: 1 hit in 100 covers 99 misses
- At 2¢ per share: 1 hit in 50 covers 49 misses
- Real hit rate with NOAA data: 4-6% on well-selected brackets

**Key Insight**: Weather models update faster than Polymarket prices.
NOAA 12-hour forecast is significantly more accurate than the market
implies for extreme-but-possible temperature brackets.

### Strategy B: Spread Arbitrage (The Consistent Grind)

**Concept**: When YES + NO < $1.00 on a guaranteed binary outcome, buy BOTH
sides and pocket the spread at resolution.

**Example** (from the article):
- Market: "Wellington 20°C on March 19"
- YES = $0.002, NO = $0.994
- YES + NO = $0.996 (gap = $0.004)
- You buy both sides: 15,000 share pairs at $0.996 each = $14,940
- At resolution, one side pays $1.00: guaranteed profit = $0.004 × 15,000 = $60
- Run this across 50+ markets per day = $3,000/day = ~$30,000/month

**Key Insight**: Thinly traded weather markets have persistent spreads
because almost nobody is arbing them. This requires ZERO prediction ability.

## 5. Why This Works — The Structural Edge

| Factor                         | Why Weather Markets Are Mispriced          |
|--------------------------------|--------------------------------------------|
| Retail doesn't understand      | Narrow brackets confuse casual bettors     |
| Thin liquidity                 | Market makers don't bother with $10K vol   |
| NOAA updates faster            | Forecast refreshes >> market re-pricing    |
| Almost no automation           | Crypto bots don't touch weather            |
| Multiple independent cities    | 50+ cities = 50+ independent edges/day     |
| Seasonal patterns              | Weather follows physics; markets don't     |

## 6. Easiest Bot Implementation Plan

### Architecture: Python Script + Cron + Polymarket API + NOAA

This is the MINIMUM viable approach — no Go, no Temporal, no gRPC.
A single Python script that runs every 90 seconds.

```
┌─────────────────────────────────────────────────────┐
│                  weather_bot.py                       │
│                                                       │
│  1. FETCH NOAA forecast for each city                │
│  2. FETCH Polymarket weather markets (prices)        │
│  3. COMPUTE edge for each bracket                    │
│     Strategy A: P_model vs P_market                  │
│     Strategy B: YES + NO < $0.997?                   │
│  4. FILTER by min edge threshold                     │
│  5. EXECUTE trades via Polymarket CLOB API           │
│  6. LOG to file + Telegram alert                     │
└─────────────────────────────────────────────────────┘
     │          │           │
     ▼          ▼           ▼
  NOAA API  Polymarket   Telegram
 (free)    CLOB API      Bot API
```

### Phase 1: Data Layer (Day 1-2) — No Trading

**NOAA/Weather Data Sources (all free):**

| Source                  | API                        | What You Get                    |
|-------------------------|----------------------------|----------------------------------|
| Open-Meteo              | api.open-meteo.com         | Free, no key, hourly forecasts   |
| NOAA NWS API            | api.weather.gov            | US cities, detailed forecasts    |
| OpenWeatherMap          | openweathermap.org/api     | Free tier: 1K calls/day          |
| Visual Crossing          | visualcrossing.com        | Historical + forecast data       |

**Open-Meteo is the best starting point** — completely free, no API key,
hourly temperature forecasts for any global city, includes multiple weather
models (GFS, ECMWF, etc.).

```python
# Example: Get Seoul forecast from Open-Meteo
import requests

def get_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "temperature_unit": "celsius",
        "forecast_days": 2,
        "models": "gfs_seamless,ecmwf_ifs025"  # multiple models = better accuracy
    }
    r = requests.get(url, params=params)
    return r.json()
```

**Polymarket Market Data:**

```python
# Polymarket CLOB API — no auth needed for reading
CLOB_API = "https://clob.polymarket.com"

def get_weather_markets():
    # GET /markets?tag=weather
    # Returns all weather markets with current prices
    r = requests.get(f"{CLOB_API}/markets", params={"tag": "weather"})
    return r.json()

def get_market_prices(token_id):
    # GET /prices?token_id=XXX
    r = requests.get(f"{CLOB_API}/prices", params={"token_id": token_id})
    return r.json()
```

### Phase 2: Signal Generation (Day 3-4) — Paper Trading

**Strategy A Logic (ColdMath):**
```python
def coldmath_signal(forecast_temp, market_brackets):
    opportunities = []
    for bracket in market_brackets:
        # bracket = {"temp": 28, "yes_price": 0.01, "no_price": 0.95}
        # Compute probability from weather model
        # Using CDF of forecast error (typically σ=1.5°C for 24h forecast)
        import scipy.stats as stats
        sigma = 1.5  # °C forecast standard deviation (24h out)
        
        # P(actual >= bracket_temp | forecast = forecast_temp)
        p_model = 1 - stats.norm.cdf(
            bracket["temp"] - forecast_temp, 
            loc=0, 
            scale=sigma
        )
        
        p_market = bracket["yes_price"]
        edge = p_model - p_market
        
        # Only enter if edge is significant
        if edge > 0.05 and p_market < 0.02:  # ultra-low brackets only
            opportunities.append({
                "bracket": bracket,
                "p_model": p_model,
                "p_market": p_market,
                "edge": edge,
                "strategy": "coldmath"
            })
    return opportunities
```

**Strategy B Logic (Spread Arbitrage):**
```python
def spread_signal(market_brackets):
    opportunities = []
    for bracket in market_brackets:
        yes_price = bracket["yes_price"]
        no_price = bracket["no_price"]
        spread = 1.0 - (yes_price + no_price)
        
        if spread > 0.003:  # minimum $0.003 spread to be worth it
            opportunities.append({
                "bracket": bracket,
                "spread": spread,
                "cost_per_pair": yes_price + no_price,
                "profit_per_pair": spread,
                "strategy": "spread_arb"
            })
    return opportunities
```

### Phase 3: Execution (Day 5-7) — Live with $50

**Polymarket CLOB Trading:**

Requires:
1. Ethereum/Polygon wallet (private key)
2. USDC.e on Polygon for trading
3. POL for gas fees
4. API key from Polymarket (register at polymarket.com)

```python
# Using py-clob-client (official Polymarket Python SDK)
# pip install py-clob-client

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType

client = ClobClient(
    host="https://clob.polymarket.com",
    key="YOUR_PRIVATE_KEY",
    chain_id=137,  # Polygon
    funder="YOUR_PUBLIC_ADDRESS"
)

# Place a buy order for YES on a temperature bracket
order_args = OrderArgs(
    price=0.01,        # 1 cent
    size=1000,         # 1000 shares ($10 position)
    side="BUY",
    token_id="TOKEN_ID_OF_YES"
)
signed_order = client.create_order(order_args)
client.post_order(signed_order, OrderType.GTC)
```

### Phase 4: Monitoring & Optimization (Week 2+)

- Telegram bot for trade alerts and P/L tracking
- AutoResearch: re-evaluate which cities/brackets are most profitable weekly
- Scale position sizes after consistent green weeks
- Add more cities as edge is validated

## 7. Risk Management — Maximizing Win Rate, Minimizing Losses

### Hard Rules (from the article + our analysis):

| Rule                         | Value           | Why                                    |
|------------------------------|-----------------|----------------------------------------|
| Max position per trade       | $10-$25        | Preserve capital for volume            |
| Daily loss limit              | $50-$100       | Stop bleeding on bad weather days      |
| Entry threshold (ColdMath)   | YES < 2¢       | Ensure 50x+ payout on hit             |
| Min spread (Spread Arb)       | > $0.003       | Cover fees + buffer                    |
| Max trades per run            | 8-12            | Don't over-concentrate                 |
| Scan frequency                | 90 seconds      | Fast enough, not API-abusive           |
| Never chase losses            | —               | ONE emotional trade can wipe a week    |
| Diversify across 10+ cities   | —               | Independent weather = independent risk |

### Win Rate Optimization:

**Strategy A (ColdMath) expected performance:**
- Win rate: 4-6% per bracket
- Average win: 50x-1000x on position
- Average loss: 1x on position
- Expected value per trade: ~0.04 × 100 - 0.96 × 1 = +$3.04 per $1 risked
- This is MASSIVELY positive EV IF your weather model is accurate

**Strategy B (Spread Arb) expected performance:**
- Win rate: 100% (guaranteed by math)
- Average profit per pair: $0.003-$0.010
- Volume: 50-100 markets/day × $100-500 per market
- Expected daily: $15-$60/day at $500 positions, $100-$300/day at $5K positions
- This is LOWER variance but LOWER return per dollar

**Combined portfolio:**
- Strategy B provides consistent daily income (pays for losses)
- Strategy A provides occasional large wins (drives total profit)
- This is the optimal portfolio structure

### Loss Minimization:

1. **Don't trade markets with < $5K volume** — they may never resolve or have
   resolution errors
2. **Use multiple weather models** — GFS + ECMWF + NAM consensus reduces
   forecast error from σ=1.5°C to σ=1.0°C
3. **Only trade 24h-out forecasts** — 7-day forecasts have σ=3-5°C, too noisy
4. **Skip extreme weather events** — hurricanes, heat waves = model uncertainty
5. **Use Kelly Criterion for position sizing**: f = (bp - q) / b where b = odds,
   p = model probability, q = 1-p. In practice: 1-2% of bankroll per trade.

## 8. City Priority List

Ranked by expected mispricing severity (thin markets + extreme temps = edge):

| Priority | City       | Why It Leaks Edge                              |
|----------|------------|------------------------------------------------|
| 1        | Wellington  | Southern hemisphere, thin volume, variable     |
| 2        | Ankara      | Continental climate, wide swings              |
| 3        | Lucknow     | Extreme heat brackets underpriced             |
| 4        | Moscow      | Cold extremes, thin volume                     |
| 5        | Chicago     | Famously variable, wide bracket spreads       |
| 6        | Helsinki    | Northern, thin volume, cold extremes           |
| 7        | Dallas/Houston | Hot extremes but higher volume              |
| 8        | Denver      | Mountain variability                           |
| 9        | Buenos Aires | Southern hemisphere, thin                     |
| 10       | Lagos/Jeddah | Tropical extremes, thin volume               |

## 9. Implementation Timeline

| Day   | Milestone                                      | Status  |
|-------|------------------------------------------------|---------|
| 1-2   | Weather data fetching (Open-Meteo + NOAA)       | TODO    |
| 3-4   | Polymarket market data + paper trading signals   | TODO    |
| 5-7   | Live execution with $50 on Strategy B (spread)  | TODO    |
| 8-10  | Add Strategy A (ColdMath) with $50               | TODO    |
| 11-14 | Telegram alerts + daily P/L tracking             | TODO    |
| 15-21 | AutoResearch: weekly strategy parameter tuning    | TODO    |
| 22-30 | Scale capital to $200-500 if profitable          | TODO    |

## 10. Comparison: Kimi Claw vs. Our Custom Python Bot

| Aspect             | Kimi Claw (Article)        | Custom Python Bot           |
|--------------------|----------------------------|------------------------------|
| Setup time         | 45 min                     | 3-5 days                    |
| Coding required    | None (plain English)       | Python intermediate          |
| Cost               | VPS $10/mo + Kimi API fees | VPS $10/mo + free APIs      |
| Customization      | Limited to clawhub skills  | Full control                 |
| Transparency       | Black box                  | Full visibility              |
| Weather model      | Unclear (Kimi decides)      | You choose (Open-Meteo, etc) |
| Risk control       | "Safeguards enabled"       | Exact Kelly sizing + limits  |
| Speed              | Claude/Kimi latency        | Direct API calls, faster     |
| Monthly cost       | $30-100 (Kimi API usage)    | $10 (VPS only)              |

**Recommendation**: Start with custom Python. You get:
- Exact control over weather model selection and sigma calibration
- Lower ongoing cost
- Better understanding of your own edge
- No dependency on third-party AI agent reliability

Kimi Claw is faster to start but you're trusting a black box with your money.

## 11. Key APIs and Tools Summary

| Tool/API           | URL                            | Cost    | Purpose              |
|---------------------|--------------------------------|---------|----------------------|
| Open-Meteo          | api.open-meteo.com             | Free    | Weather forecasts    |
| NOAA NWS            | api.weather.gov                | Free    | US city forecasts    |
| Polymarket CLOB     | clob.polymarket.com            | Free    | Market data + trades |
| py-clob-client      | pip install py-clob-client     | Free    | Python SDK           |
| Telegram Bot API    | api.telegram.org              | Free    | Alerts/monitoring    |
| Polygon RPC         | polygon-rpc.com               | Free    | Blockchain reads     |

## 12. The #1 Most Important Thing

The edge is NOT in predicting weather better than a meteorologist.
The edge is in acting on weather data FASTER than Polymarket prices adjust.

Weather models update every 1-6 hours. Polymarket manual bettors update
irregularly — sometimes hours or days late. The bot closes that gap.

This is the same principle as the existing speed-gap arbitrage in the
main branch — but applied to a market segment where the gap is MUCH wider
and the competition is MUCH thinner.