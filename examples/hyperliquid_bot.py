"""
hyperliquid_bot.py — Example: wiring PodLogger into a Hyperliquid perps bot.

Shows the integration pattern for wiring PodLogger into a Hyperliquid perps bot.

Replace the placeholder signal logic with your own. The logging calls are
what matter — those are copy-paste ready.

Requirements:
    pip install requests python-dotenv

Usage:
    cp .env.example .env  # fill in your credentials
    python3 examples/hyperliquid_bot.py
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load from .env in repo root
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent dir to path so we can import reppo_sdk
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from reppo_sdk import PodLogger

# ─── Config ──────────────────────────────────────────────────────────────────

AGENT_ID   = os.getenv("AGENT_ID", "my-agent")
AGENT_NAME = os.getenv("AGENT_NAME", "MyHLBot")

# Markets to scan — Hyperliquid perps
MARKETS = ["BTC", "ETH", "SOL", "BNB", "SUI", "AVAX", "HYPE", "XRP", "DOGE"]

# Signal thresholds — tune these for your strategy
THRESHOLD_SCALP  = 5.0   # minimum score to open a scalp
THRESHOLD_SWING  = 6.5   # minimum score to open a swing
THRESHOLD_NEAR_MISS = 3.5  # log near-misses above this score

SCAN_INTERVAL_SECONDS = 300  # 5 minutes

# ─── Logger init ─────────────────────────────────────────────────────────────

logger = PodLogger(agent_id=AGENT_ID, agent_name=AGENT_NAME)

# ─── Hyperliquid helpers ──────────────────────────────────────────────────────

HL_API = "https://api.hyperliquid.xyz/info"

def hl_post(payload: dict) -> dict:
    """POST to Hyperliquid info endpoint."""
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        HL_API,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠️  HL API error: {e}")
        return {}


def get_mid_price(pair: str) -> float | None:
    """Get current mid price for a pair."""
    data = hl_post({"type": "allMids"})
    return float(data.get(pair, 0)) or None


def get_candles(pair: str, interval: str = "1h", count: int = 50) -> list[dict]:
    """Fetch OHLCV candles from Hyperliquid."""
    now_ms = int(time.time() * 1000)
    interval_ms = {"15m": 900_000, "1h": 3_600_000, "4h": 14_400_000}
    ms = interval_ms.get(interval, 3_600_000)
    start_ms = now_ms - (count * ms)
    data = hl_post({
        "type": "candleSnapshot",
        "req": {"coin": pair, "interval": interval, "startTime": start_ms, "endTime": now_ms}
    })
    return data if isinstance(data, list) else []


def get_btc_dominance() -> float | None:
    """Approximate BTC dominance from prices (or return None if unavailable)."""
    # In production: fetch from CoinGecko or similar
    return None


# ─── Signal engine ────────────────────────────────────────────────────────────

def compute_ema(prices: list[float], period: int) -> float | None:
    """Exponential moving average."""
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema


def compute_rsi(prices: list[float], period: int = 14) -> float | None:
    """RSI from close prices."""
    if len(prices) < period + 1:
        return None
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d for d in deltas if d > 0]
    losses = [-d for d in deltas if d < 0]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def analyze_pair(pair: str) -> dict:
    """
    Compute signals for a single pair.
    Returns a dict with score, side, signals, and reasons.

    This is where YOUR signal logic lives. The example below is a simplified
    multi-timeframe EMA + RSI stack — replace with your own signals.
    """
    candles_1h = get_candles(pair, "1h", 60)
    candles_4h = get_candles(pair, "4h", 30)

    if not candles_1h or not candles_4h:
        return {"score": 0, "side": None, "signals": {}, "reasons": ["no data"], "atr_pct": 1.0}

    closes_1h = [float(c["c"]) for c in candles_1h]
    closes_4h = [float(c["c"]) for c in candles_4h]
    current_price = closes_1h[-1]

    # EMAs
    ema9_1h  = compute_ema(closes_1h, 9)
    ema21_1h = compute_ema(closes_1h, 21)
    ema50_4h = compute_ema(closes_4h, 50)

    # RSI
    rsi_1h = compute_rsi(closes_1h)

    # ATR (simplified)
    highs = [float(c["h"]) for c in candles_1h[-14:]]
    lows  = [float(c["l"]) for c in candles_1h[-14:]]
    atr = sum(h - l for h, l in zip(highs, lows)) / len(highs)
    atr_pct = round((atr / current_price) * 100, 3)

    score = 0.0
    votes_long = 0
    votes_short = 0
    reasons = []
    signals = {
        "rsi_1h": rsi_1h,
        "ema9_1h": ema9_1h,
        "ema21_1h": ema21_1h,
        "ema50_4h": ema50_4h,
        "atr_pct": atr_pct,
        "current_price": current_price,
        "reasons": [],
    }

    # 1H EMA stack bullish
    if ema9_1h and ema21_1h and ema9_1h > ema21_1h:
        score += 1.5; votes_long += 1
        reasons.append("1H EMA9 > EMA21 (bullish)")
    elif ema9_1h and ema21_1h and ema9_1h < ema21_1h:
        score += 1.5; votes_short += 1
        reasons.append("1H EMA9 < EMA21 (bearish)")

    # 4H trend
    if ema50_4h and current_price > ema50_4h:
        score += 2.0; votes_long += 2
        reasons.append("Price above 4H EMA50 (uptrend)")
    elif ema50_4h and current_price < ema50_4h:
        score += 2.0; votes_short += 2
        reasons.append("Price below 4H EMA50 (downtrend)")

    # RSI signals
    if rsi_1h is not None:
        if rsi_1h < 30:
            score += 2.0; votes_long += 2
            reasons.append(f"RSI oversold ({rsi_1h:.1f})")
        elif rsi_1h > 70:
            score += 2.0; votes_short += 2
            reasons.append(f"RSI overbought ({rsi_1h:.1f})")
        elif rsi_1h < 45:
            score += 0.5; votes_long += 1
            reasons.append(f"RSI leaning long ({rsi_1h:.1f})")
        elif rsi_1h > 55:
            score += 0.5; votes_short += 1
            reasons.append(f"RSI leaning short ({rsi_1h:.1f})")

    # Determine direction
    if votes_long == 0 and votes_short == 0:
        side = None
    else:
        side = "long" if votes_long >= votes_short else "short"

    signals["reasons"] = reasons
    return {
        "score": round(score, 2),
        "side": side,
        "signals": signals,
        "reasons": reasons,
        "atr_pct": atr_pct,
    }


# ─── Main bot loop ────────────────────────────────────────────────────────────

def run():
    print(f"🤖 {AGENT_NAME} starting — Hyperliquid perps | {len(MARKETS)} markets")
    print(f"   Thresholds: scalp ≥{THRESHOLD_SCALP} | swing ≥{THRESHOLD_SWING}")
    print(f"   Near-miss logging ≥{THRESHOLD_NEAR_MISS}")
    print(f"   Pod data → {logger.data_dir}\n")

    open_positions: dict[str, dict] = {}

    while True:
        ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        print(f"\n── Scan cycle {ts} ──────────────────────────────")

        # ── T3: log the scan cycle ────────────────────────────────────────────
        logger.log_scan(
            pairs_scanned=MARKETS,
            regime="ranging",           # replace with your regime detection
            btc_dominance=get_btc_dominance(),
        )

        for pair in MARKETS:
            result = analyze_pair(pair)
            score  = result["score"]
            side   = result["side"]
            signals = result["signals"]
            atr_pct = result["atr_pct"]

            if score == 0 or side is None:
                continue

            # ── T1: entry signal met → log trade ─────────────────────────────
            if score >= THRESHOLD_SWING and pair not in open_positions:
                price = get_mid_price(pair)
                if not price:
                    continue

                # Conviction-scaled leverage (adjust to your risk params)
                leverage = 3 if score < 6.5 else (5 if score < 8.0 else 7)
                size_usd = 100.0  # replace with your position sizing logic

                print(f"  ✅ ENTRY: {side.upper()} {pair} @ {price:.4f} | score={score} | lev={leverage}x")

                # ── THIS IS THE LOGGING CALL — copy this into your bot ────────
                logger.log_trade(
                    pair=pair,
                    side=side,
                    entry_price=price,
                    size_usd=size_usd,
                    leverage=leverage,
                    signals=signals,
                    score=score,
                    strategy="swing",
                )
                # ─────────────────────────────────────────────────────────────

                open_positions[pair] = {"price": price, "side": side, "score": score}

                # TODO: your actual order submission to Hyperliquid here
                # e.g. hl_executor.open_position(pair, side, size_usd, leverage)

            # ── T2: near-miss → score above threshold_near_miss but below entry
            elif THRESHOLD_NEAR_MISS <= score < THRESHOLD_SWING:

                # ── THIS IS THE NEAR-MISS LOGGING CALL ───────────────────────
                logger.log_near_miss(
                    pair=pair,
                    side=side,
                    score=score,
                    threshold=THRESHOLD_SWING,
                    signals=signals,
                    reason_not_traded=f"score_{score}_below_threshold_{THRESHOLD_SWING}",
                )
                # ─────────────────────────────────────────────────────────────

        # ── T1: check open positions for exits ───────────────────────────────
        for pair, pos in list(open_positions.items()):
            price = get_mid_price(pair)
            if not price:
                continue

            entry = pos["price"]
            pnl_pct = (price - entry) / entry if pos["side"] == "long" else (entry - price) / entry

            # Simple exit logic — replace with your patience/TP/SL logic
            if abs(pnl_pct) > 0.015 or True:  # remove `or True` in production
                close_reason = "take_profit" if pnl_pct > 0 else "patience_exit"
                icon = "🟢" if pnl_pct > 0 else "🔴"
                print(f"  {icon} CLOSE: {pair} | PnL={pnl_pct*100:.2f}% | {close_reason}")

                # ── THIS IS THE CLOSE LOGGING CALL ───────────────────────────
                logger.log_close(
                    pair=pair,
                    exit_price=price,
                    pnl_pct=round(pnl_pct, 6),
                    hold_hours=0.5,  # replace with actual hold time
                    close_reason=close_reason,
                    entry_price=entry,
                    side=pos["side"],
                )
                # ─────────────────────────────────────────────────────────────

                del open_positions[pair]

                # TODO: your actual close order to Hyperliquid here

        # ── Buffer status summary ─────────────────────────────────────────────
        counts = logger.buffer_counts()
        print(f"\n  📊 Buffers: T1={counts['t1_trades']} trades | T2={counts['t2_near_misses']} near-misses | T3={counts['t3_scans']} scans")

        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
