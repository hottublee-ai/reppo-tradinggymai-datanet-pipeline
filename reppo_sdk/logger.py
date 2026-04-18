"""
PodLogger — Drop-in instrumentation for any trading bot.

Usage:
    from reppo_sdk import PodLogger

    logger = PodLogger(agent_id="my-agent", agent_name="MyBot")
    logger.log_trade(pair="BTC", side="long", entry_price=84500, ...)
    logger.log_near_miss(pair="ETH", side="long", score=4.8, ...)
    logger.log_close(pair="BTC", exit_price=85200, pnl_pct=0.0083, ...)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


class PodLogger:
    """
    Lightweight logger that writes T1/T2/T3 buffer files for pod generation.
    Drop this into any trading bot — exchange-agnostic, language-agnostic schema.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        data_dir: str | Path | None = None,
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name

        # Default data dir: ./data/<agent_name>/
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / agent_name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.t1_path = self.data_dir / "tier1_buffer.jsonl"
        self.t2_path = self.data_dir / "tier2_buffer.jsonl"
        self.t3_path = self.data_dir / "tier3_buffer.jsonl"

    def _ts(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _append(self, path: Path, record: dict):
        with open(path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def log_trade(
        self,
        pair: str,
        side: str,                  # "long" | "short"
        entry_price: float,
        size_usd: float,
        leverage: int,
        signals: dict,              # {"rsi_1h": 28.4, "obi": 0.61, "reasons": [...]}
        score: float,
        strategy: str = "swing",    # "swing" | "scalp" | "sniper"
        take_profit_pct: float | None = None,
        stop_loss_pct: float | None = None,
        extra: dict | None = None,
    ):
        """Log an executed trade entry (T1)."""
        record = {
            "type": "open",
            "ts": self._ts(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "pair": pair,
            "side": side,
            "entry_price": entry_price,
            "size_usd": size_usd,
            "leverage": leverage,
            "score": score,
            "strategy": strategy,
            "signals": signals,
            "take_profit_pct": take_profit_pct,
            "stop_loss_pct": stop_loss_pct,
        }
        if extra:
            record.update(extra)
        self._append(self.t1_path, record)

    def log_close(
        self,
        pair: str,
        exit_price: float,
        pnl_pct: float,
        hold_hours: float,
        close_reason: str,          # "take_profit" | "patience_exit" | "timeout" | "manual"
        entry_price: float | None = None,
        side: str = "long",
        extra: dict | None = None,
    ):
        """Log a trade close (T1)."""
        record = {
            "type": "close",
            "ts": self._ts(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "pair": pair,
            "side": side,
            "exit_price": exit_price,
            "entry_price": entry_price,
            "pnl_pct": pnl_pct,
            "hold_hours": hold_hours,
            "close_reason": close_reason,
        }
        if extra:
            record.update(extra)
        self._append(self.t1_path, record)

    def log_near_miss(
        self,
        pair: str,
        side: str,
        score: float,
        threshold: float,
        signals: dict,
        reason_not_traded: str | None = None,
        tier: int = 2,
        extra: dict | None = None,
    ):
        """
        Log a near-miss signal (T2) — evaluated but not traded.
        These are the most valuable records for Reppo training.
        Capture anything that scored within 2 points of your threshold.
        """
        record = {
            "ts": self._ts(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "pair": pair,
            "side": side,
            "score": score,
            "threshold": threshold,
            "tier": tier,
            "reason_not_traded": reason_not_traded or f"score_{score}_below_threshold_{threshold}",
            "signals": signals,
        }
        if extra:
            record.update(extra)
        self._append(self.t2_path, record)

    def log_scan(
        self,
        pairs_scanned: list[str],
        regime: str,                # "trending" | "ranging" | "volatile"
        btc_dominance: float | None = None,
        market_notes: str | None = None,
        extra: dict | None = None,
    ):
        """Log a market scan cycle (T3)."""
        record = {
            "ts": self._ts(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "pairs_scanned": pairs_scanned,
            "pairs_count": len(pairs_scanned),
            "regime": regime,
            "btc_dominance": btc_dominance,
            "market_notes": market_notes,
        }
        if extra:
            record.update(extra)
        self._append(self.t3_path, record)

    def buffer_counts(self) -> dict:
        """Return current record counts for each buffer."""
        def count(path):
            if not path.exists():
                return 0
            return sum(1 for _ in open(path) if _.strip())

        return {
            "t1_trades": count(self.t1_path),
            "t2_near_misses": count(self.t2_path),
            "t3_scans": count(self.t3_path),
        }
