"""
basic_bot.py — Minimal example showing how to wire PodLogger into any trading bot.

This is a skeleton — replace the placeholder logic with your actual signal engine.
"""

import time
import random
from reppo_sdk import PodLogger

# Initialize logger — one per agent
logger = PodLogger(agent_id="my-agent-001", agent_name="MyBot")

PAIRS = ["BTC", "ETH", "SOL", "SUI", "AVAX"]
SIGNAL_THRESHOLD = 5.5


def compute_signals(pair: str) -> dict:
    """Your signal engine goes here. This returns a mock."""
    return {
        "rsi_1h": random.uniform(10, 90),
        "obi": random.uniform(-1, 1),
        "atr_pct": random.uniform(0.3, 2.0),
        "reasons": ["RSI oversold", "OBI buy pressure"] if random.random() > 0.5 else ["EMA mixed", "VWAP below"],
    }


def score_signals(signals: dict) -> float:
    """Your scoring logic goes here."""
    score = 3.0
    if signals["rsi_1h"] < 30:
        score += 1.5
    if signals["obi"] > 0.4:
        score += 1.0
    return round(score, 2)


def run_bot():
    open_positions = {}

    while True:
        # Log a scan cycle (T3)
        logger.log_scan(
            pairs_scanned=PAIRS,
            regime="ranging",
            btc_dominance=57.4,
        )

        for pair in PAIRS:
            signals = compute_signals(pair)
            score = score_signals(signals)

            if score >= SIGNAL_THRESHOLD:
                # Entry signal — log the trade (T1)
                entry_price = random.uniform(80000, 90000) if pair == "BTC" else random.uniform(100, 5000)
                logger.log_trade(
                    pair=pair,
                    side="long",
                    entry_price=entry_price,
                    size_usd=100.0,
                    leverage=5,
                    signals=signals,
                    score=score,
                    strategy="swing",
                )
                open_positions[pair] = entry_price
                print(f"  ✅ ENTERED {pair} @ {entry_price:.2f} (score {score})")

            elif score >= 4.0:
                # Near-miss — log it (T2) — this is valuable training data!
                logger.log_near_miss(
                    pair=pair,
                    side="long",
                    score=score,
                    threshold=SIGNAL_THRESHOLD,
                    signals=signals,
                )

            # Simulate closing open positions
            if pair in open_positions:
                pnl = random.uniform(-0.02, 0.05)
                logger.log_close(
                    pair=pair,
                    exit_price=open_positions[pair] * (1 + pnl),
                    pnl_pct=pnl,
                    hold_hours=random.uniform(2, 24),
                    close_reason="take_profit" if pnl > 0 else "patience_exit",
                    entry_price=open_positions[pair],
                )
                del open_positions[pair]
                print(f"  {'🟢' if pnl > 0 else '🔴'} CLOSED {pair} | PnL: {pnl*100:.2f}%")

        counts = logger.buffer_counts()
        print(f"  📊 Buffers: T1={counts['t1_trades']} | T2={counts['t2_near_misses']} | T3={counts['t3_scans']}")
        time.sleep(60)  # scan every minute


if __name__ == "__main__":
    print("🤖 MyBot starting — logging to Reppo pod buffers...")
    run_bot()
