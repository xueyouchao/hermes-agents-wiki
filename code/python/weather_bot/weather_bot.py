# Weather Arbitrage Bot — Skeletal Implementation

"""
weather_bot.py — Minimum viable Polymarket weather arbitrage bot

Strategy A: ColdMath — Buy ultra-low YES on mispriced temperature brackets
Strategy B: Spread Arb — Buy YES+NO when their sum < $1.00

Runs every 90 seconds via cron.
"""

import requests
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

CONFIG = {
    # Weather data
    "open_meteo_base": "https://api.open-meteo.com/v1/forecast",
    "forecast_days": 2,  # Only trade 24-48h out
    
    # Polymarket
    "clob_api": "https://clob.polymarket.com",
    "gamma_api": "https://gamma-api.polymarket.com",
    
    # Strategy A (ColdMath)
    "coldmath_max_yes_price": 0.02,  # Only buy YES if priced ≤ 2¢
    "coldmath_min_edge": 0.05,       # Model probability must exceed market by 5%
    "coldmath_forecast_sigma": 1.2,  # °C standard deviation (conservative)
    "coldmath_max_position_usd": 25,
    
    # Strategy B (Spread Arb)
    "spread_min_gap": 0.003,         # Min spread in $ per share pair
    "spread_max_position_usd": 500,  # Per market
    "spread_max_markets_per_run": 10,
    
    # Risk
    "max_daily_loss_usd": 100,
    "scan_interval_seconds": 90,
    
    # Logging
    "log_dir": Path(__file__).parent / "logs",
    "telegram_bot_token": None,  # Set via env var TELEGRAM_BOT_TOKEN
    "telegram_chat_id": None,   # Set via env var TELEGRAM_CHAT_ID
}

# ─── City Coordinates (lat, lon) ─────────────────────────────────────────────

CITIES = {
    "Seoul": (37.5665, 126.9780),
    "London": (51.5074, -0.1278),
    "Shanghai": (31.2304, 121.4737),
    "Tokyo": (35.6762, 139.6503),
    "Chicago": (41.8781, -87.6298),
    "NYC": (40.7128, -74.0060),
    "Ankara": (39.9334, 32.8597),
    "Dallas": (32.7767, -96.7970),
    "Wellington": (-41.2865, 174.7762),
    "Sao Paulo": (-23.5505, -46.6333),
    "Mumbai": (19.0760, 72.8777),
    "Lucknow": (26.8467, 80.9462),
    "Moscow": (55.7558, 37.6173),
    "Helsinki": (60.1699, 24.9384),
    "Buenos Aires": (-34.6037, -58.3816),
    "Denver": (39.7392, -104.9903),
    "Istanbul": (41.0082, 28.9784),
    "Singapore": (1.3521, 103.8198),
    "Miami": (25.7617, -80.1918),
    "Lagos": (6.5244, 3.3792),
}

# ─── Weather Data ─────────────────────────────────────────────────────────────

def fetch_forecast(city_name, lat, lon):
    """Fetch hourly temperature forecast from Open-Meteo using multiple models."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "temperature_unit": "celsius",
        "forecast_days": CONFIG["forecast_days"],
        "models": "gfs_seamless,ecmwf_ifs025,best_match",
    }
    try:
        r = requests.get(CONFIG["open_meteo_base"], params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        result = {
            "city": city_name,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "models": {},
        }
        
        # Parse hourly data
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        
        if not times:
            logging.warning(f"No hourly data for {city_name}")
            return None
        
        # Find max and min temps for each day
        from collections import defaultdict
        daily_temps = defaultdict(list)
        for i, t in enumerate(times):
            date = t[:10]
            for model_key in data:
                if model_key.startswith("hourly_") and "temperature" in model_key:
                    temps = data[model_key]
                    if i < len(temps) and temps[i] is not None:
                        daily_temps[date].append(temps[i])
        
        # Use the primary best_match model for main forecast
        primary_temps = hourly.get("temperature_2m", [])
        for i, t in enumerate(times):
            date = t[:10]
            if date not in result["models"]:
                result["models"][date] = {"hourly": [], "high": None, "low": None}
            if i < len(primary_temps) and primary_temps[i] is not None:
                result["models"][date]["hourly"].append(primary_temps[i])
        
        for date, model_data in result["models"].items():
            if model_data["hourly"]:
                model_data["high"] = max(model_data["hourly"])
                model_data["low"] = min(model_data["hourly"])
        
        return result
    except Exception as e:
        logging.error(f"Weather fetch failed for {city_name}: {e}")
        return None


# ─── Polymarket Data ──────────────────────────────────────────────────────────

def fetch_weather_markets():
    """Fetch all Polymarket weather markets with current prices."""
    try:
        # Gamma API provides event-level data
        r = requests.get(
            f"{CONFIG['gamma_api']}/events",
            params={"tag": "weather", "closed": False, "limit": 250},
            timeout=15,
        )
        r.raise_for_status()
        events = r.json()
        
        markets = []
        for event in events:
            for market in event.get("markets", []):
                markets.append({
                    "question": market.get("question", ""),
                    "condition_id": market.get("conditionId", ""),
                    "token_id_yes": market.get("clobTokenIds", ["", ""])[0] if market.get("clobTokenIds") else "",
                    "token_id_no": market.get("clobTokenIds", ["", ""])[1] if market.get("clobTokenIds") else "",
                    "yes_price": float(market.get("outcomePrices", "0,0").split(",")[0] or 0),
                    "no_price": float(market.get("outcomePrices", "0,0").split(",")[1] or 0),
                    "volume": float(market.get("volume", 0)),
                    "end_date": market.get("endDate", ""),
                })
        
        logging.info(f"Fetched {len(markets)} weather markets")
        return markets
    except Exception as e:
        logging.error(f"Polymarket fetch failed: {e}")
        return []


def parse_temp_market(question):
    """Extract city, date, and temperature from a market question.
    
    Examples:
    - "Will the highest temperature in Seoul be 18°C on April 27?"
    - "Will the highest temperature in Dallas be 88°F or higher on April 27?"
    """
    import re
    
    # Pattern: ...in <CITY> be <TEMP>°C/F [or higher] on <DATE>?
    pattern = r"(?:highest|lowest)\s+temperature\s+in\s+(.+?)\s+be\s+([\d.]+)°([CF])(?:\s+or\s+higher)?\s+on\s+(.+?)\?"
    match = re.search(pattern, question, re.IGNORECASE)
    
    if not match:
        return None
    
    city = match.group(1).strip()
    temp = float(match.group(2))
    unit = match.group(3).upper()
    date_str = match.group(4).strip()
    
    # Convert F to C if needed
    if unit == "F":
        temp_c = (temp - 32) * 5 / 9
    else:
        temp_c = temp
    
    return {
        "city": city,
        "temp_c": round(temp_c, 1),
        "temp_original": temp,
        "unit": unit,
        "date": date_str,
    }


# ─── Signal Generation ───────────────────────────────────────────────────────

def generate_coldmath_signals(forecasts, markets):
    """Strategy A: Find ultra-low brackets where model probability >> market price."""
    from scipy import stats
    
    signals = []
    sigma = CONFIG["coldmath_forecast_sigma"]
    
    for market in markets:
        parsed = parse_temp_market(market["question"])
        if not parsed:
            continue
        
        city = parsed["city"]
        temp_bracket = parsed["temp_c"]
        
        # Find matching forecast
        forecast = forecasts.get(city)
        if not forecast:
            continue
        
        # Get forecast high/low for that date
        date_key = parsed["date"].replace(" ", "-")  # rough normalization
        model_data = forecast["models"].get(date_key)
        if not model_data or model_data.get("high") is None:
            # Fallback: use any available date
            available = list(forecast["models"].values())
            if available:
                model_data = available[0]
            else:
                continue
        
        # Determine if this is a "highest" or "lowest" market
        is_high = "highest" in market["question"].lower()
        forecast_val = model_data["high"] if is_high else model_data["low"]
        
        # Compute P(actual >= bracket | forecast = forecast_val)
        if is_high:
            p_model = 1 - stats.norm.cdf(temp_bracket - forecast_val, loc=0, scale=sigma)
        else:
            p_model = stats.norm.cdf(temp_bracket - forecast_val, loc=0, scale=sigma)
        
        p_market = market["yes_price"]
        edge = p_model - p_market
        
        # Filter: only ultra-low brackets with significant edge
        if p_market <= CONFIG["coldmath_max_yes_price"] and edge >= CONFIG["coldmath_min_edge"]:
            signals.append({
                "strategy": "coldmath",
                "market": market,
                "parsed": parsed,
                "p_model": round(p_model, 4),
                "p_market": round(p_market, 4),
                "edge": round(edge, 4),
                "forecast_val": forecast_val,
                "action": "BUY_YES",
                "position_usd": min(CONFIG["coldmath_max_position_usd"], round(edge * 1000, 2)),
            })
    
    return signals


def generate_spread_signals(markets):
    """Strategy B: Find markets where YES + NO < $1.00."""
    signals = []
    
    for market in markets:
        gap = 1.0 - (market["yes_price"] + market["no_price"])
        
        if gap >= CONFIG["spread_min_gap"] and market["volume"] > 5000:
            signals.append({
                "strategy": "spread_arb",
                "market": market,
                "gap": round(gap, 4),
                "cost_per_pair": round(market["yes_price"] + market["no_price"], 4),
                "profit_per_pair": round(gap, 4),
                "action": "BUY_BOTH",
                "position_usd": min(CONFIG["spread_max_position_usd"], round(gap * 50000, 2)),
            })
    
    # Sort by gap size, take top N
    signals.sort(key=lambda s: s["gap"], reverse=True)
    return signals[:CONFIG["spread_max_markets_per_run"]]


# ─── Execution (Stub — requires wallet setup) ────────────────────────────────

def execute_trade(signal):
    """Execute a trade on Polymarket CLOB.
    
    This is a STUB. To make it live:
    1. pip install py-clob-client
    2. Set PRIVATE_KEY and FUNDER_ADDRESS env vars
    3. Fund wallet with USDC.e on Polygon
    4. Uncomment the client code below
    """
    logging.info(
        f"[{signal['strategy'].upper()}] {signal['action']} | "
        f"Market: {signal['market']['question'][:60]}... | "
        f"Edge: {signal.get('edge', signal.get('gap', 0)):.4f} | "
        f"Position: ${signal['position_usd']:.2f}"
    )
    
    # ── Live execution (uncomment when ready) ──
    # from py_clob_client.client import ClobClient
    # from py_clob_client.clob_types import OrderArgs, OrderType
    # 
    # client = ClobClient(
    #     host="https://clob.polymarket.com",
    #     key=os.environ["PRIVATE_KEY"],
    #     chain_id=137,
    #     funder=os.environ["FUNDER_ADDRESS"],
    # )
    # 
    # if signal["action"] == "BUY_YES":
    #     order = OrderArgs(
    #         price=signal["p_market"],
    #         size=int(signal["position_usd"] / signal["p_market"]),
    #         side="BUY",
    #         token_id=signal["market"]["token_id_yes"],
    #     )
    #     signed = client.create_order(order)
    #     client.post_order(signed, OrderType.GTC)
    # elif signal["action"] == "BUY_BOTH":
    #     # Buy YES side
    #     yes_order = OrderArgs(
    #         price=signal["market"]["yes_price"],
    #         size=int(signal["position_usd"] * 0.5 / signal["market"]["yes_price"]),
    #         side="BUY",
    #         token_id=signal["market"]["token_id_yes"],
    #     )
    #     signed_yes = client.create_order(yes_order)
    #     client.post_order(signed_yes, OrderType.GTC)
    #     
    #     # Buy NO side
    #     no_order = OrderArgs(
    #         price=signal["market"]["no_price"],
    #         size=int(signal["position_usd"] * 0.5 / signal["market"]["no_price"]),
    #         side="BUY",
    #         token_id=signal["market"]["token_id_no"],
    #     )
    #     signed_no = client.create_order(no_order)
    #     client.post_order(signed_no, OrderType.GTC)
    
    return True


# ─── Telegram Alerts ──────────────────────────────────────────────────────────

def send_telegram(message):
    """Send a Telegram alert."""
    import os
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or CONFIG["telegram_bot_token"]
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or CONFIG["telegram_chat_id"]
    
    if not token or not chat_id:
        return
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception as e:
        logging.error(f"Telegram send failed: {e}")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def run():
    """One scan cycle."""
    logging.info("=" * 60)
    logging.info("Weather arbitrage scan starting")
    
    # 1. Fetch weather forecasts for all cities
    forecasts = {}
    for city, (lat, lon) in CITIES.items():
        forecast = fetch_forecast(city, lat, lon)
        if forecast:
            forecasts[city] = forecast
        time.sleep(0.2)  # Rate limit
    
    logging.info(f"Fetched forecasts for {len(forecasts)}/{len(CITIES)} cities")
    
    # 2. Fetch Polymarket weather markets
    markets = fetch_weather_markets()
    if not markets:
        logging.warning("No markets found, skipping")
        return
    
    # 3. Generate signals
    coldmath_signals = generate_coldmath_signals(forecasts, markets)
    spread_signals = generate_spread_signals(markets)
    
    all_signals = coldmath_signals + spread_signals
    logging.info(
        f"Signals: {len(coldmath_signals)} ColdMath + {len(spread_signals)} Spread "
        f"= {len(all_signals)} total"
    )
    
    # 4. Execute trades
    for signal in all_signals:
        try:
            execute_trade(signal)
        except Exception as e:
            logging.error(f"Trade execution failed: {e}")
    
    # 5. Send summary alert
    if all_signals:
        summary = f"*Weather Bot Scan*\n"
        summary += f"ColdMath: {len(coldmath_signals)} | Spread: {len(spread_signals)}\n"
        for s in all_signals[:5]:
            q = s["market"]["question"][:40]
            e = s.get("edge", s.get("gap", 0))
            summary += f"• {q}... edge={e:.3f}\n"
        send_telegram(summary)
    
    logging.info(f"Scan complete: {len(all_signals)} signals processed")


if __name__ == "__main__":
    # Setup logging
    CONFIG["log_dir"].mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(CONFIG["log_dir"] / "weather_bot.log"),
            logging.StreamHandler(),
        ],
    )
    
    run()