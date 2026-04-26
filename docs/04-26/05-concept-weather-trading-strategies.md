---
title: Weather Prediction Market Trading Strategies
created: 2026-04-26
updated: 2026-04-26
type: concept
tags: [prediction-market, weather-bot, kelly-criterion, ensemble-forecast]
sources: [raw/articles/polymarket-weather-bot-guillermo.md, raw/articles/polymarket-kalshi-weather-bot-suislanchez.md]
---

# Weather Prediction Market Trading Strategies

## Strategy A: ColdMath Ultra-Low Bracket

Buy YES on temperature brackets priced at 1-15 cents where the weather forecast (or ensemble) suggests a higher probability. Since exactly one bracket must resolve YES, even a 4-6% hit rate on 1-2c brackets is profitable.

**Example:** NWS says NYC high will be 78°F. The "75-80°F" bracket is at 42c (heavily priced), but the "80-85°F" bracket is at 3c. Your ensemble says there's a 15% chance of exceeding 80°F. Expected value = 0.15 * $1.00 = $0.15, cost = $0.03. Edge = 400%.

**Implemented by:** [[polymarket-weather-bot-guillermo]] (variant: buy any bracket where YES < entry_threshold)

**On platform:**
- Polymarket: Minimum price ~0.1c, so ultra-low brackets are available. Higher ROI per trade.
- Kalshi: Minimum price ~3-4c, so the ultra-low edge is smaller. Still viable at 15-25c levels.

## Strategy B: Cross-Bracket Sum Mispricing

In temperature bracket markets, exactly one bracket must resolve YES. If the sum of all YES prices < $1.00, buying all of them guarantees profit (arbitrage). More commonly, specific bracket combinations are mispriced relative to each other.

**Example:** Sum of YES prices = $0.92. Buy all brackets. Guaranteed $1.00 at resolution. Profit = $0.08.

**Implemented by:** None of the analyzed bots. This requires summing all bracket prices per event.

**Cross-platform variant:** If Polymarket and Kalshi offer similar markets but with different prices, buy low on one and sell high on the other (requires both accounts).

## Strategy C: Ensemble Probability vs Market Implied Probability

Use ensemble weather forecasts (GFS 31-member, ECMWF 51-member) to estimate the true probability of each bracket, then compare to the market's implied probability. Trade when edge exceeds a threshold.

**Implemented by:** [[polymarket-kalshi-weather-bot-suislanchez]] (signal only, no execution)

**Key formula:** `edge = model_probability - market_probability`
**Entry condition:** `|edge| > 8%`
**Sizing:** Fractional Kelly = `(win_prob * odds - lose_prob) / odds * Kelly_fraction`

## Strategy Comparison Matrix

| Aspect | Strategy A (ColdMath) | Strategy B (Cross-Bracket) | Strategy C (Ensemble Edge) |
|--------|----------------------|----------------------------|---------------------------|
| Edge source | Ultra-low prices on long-shot brackets | Structural mispricing of sum vs $1 | Ensemble vs market probability |
| Required accuracy | 4-6% hit rate sufficient | 100% guaranteed (arbitrage) | Must beat market consistently |
| Risk level | Low per trade, low hit rate | Near-zero | Medium (model risk) |
| Capital needed | Low | High (buy all brackets) | Medium |
| Frequency | Few trades per week | Rare when available | Multiple daily opportunities |
| Best platform | Polymarket (cheaper min price) | Either | Both (Kalshi for US access) |
| Weather data needed | Single deterministic forecast | None (pure price) | Ensemble forecast |

## Kelly Criterion for Prediction Markets

For a binary outcome at price `p`:
- If our probability `q > p`, buy YES
- Kelly fraction: `f = (q * (1-p) - (1-q) * p) / (1-p)` when betting YES
- Fractional Kelly (15-25% of full Kelly) reduces variance

**Daily loss limits** prevent catastrophic drawdowns during mode periods.
