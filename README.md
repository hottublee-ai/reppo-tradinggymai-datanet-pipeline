# 🧠 Reppo Pod Pipeline

**Instrument your trading bot. Generate structured data pods. Contribute to the TradingGym AI datanet. Earn Reppo rewards.**

Built by [@Hottubleed](https://x.com/Hottubleed) — the same pipeline powering [hottubleeee](https://degen.virtuals.io/agents/565) and [HotBot](https://degen.virtuals.io/agents/702) on the Virtuals DegenClaw competition.

---

## What is this?

[Reppo](https://reppo.ai) is a decentralized AI training data marketplace. Trading bots that contribute high-quality, verifiable trade data earn rewards — and help train better AI models.

This repo gives you everything you need to:

1. **Instrument** your existing trading bot to capture trade data
2. **Generate** structured IPFS pods (T1/T2/T3/T4 format)
3. **Pin** them to the TradingGym AI datanet via Pinata
4. **Submit** CIDs to Reppo every epoch

No lock-in. Works with any bot, any exchange, any language.

---

## The Pod Schema (T1–T4)

Every epoch (48h) produces 4 pods:

| Pod | Tier | What it contains |
|-----|------|-----------------|
| Pod 1 | T1 — Executed Trades | Every real entry + exit with full signal rationale |
| Pod 2 | T2 — Close Calls | Signals that scored just below threshold (near-misses) |
| Pod 3 | T3 — Scan Coverage | All markets × scan cycles + regime state |
| Pod 4 | T4 — Strategy Refinement | Synthesized lessons: loss patterns, win/loss attribution, recommendations |

T2 (near-misses) is often the most valuable tier — it shows what the bot *considered* and *why it passed*. That counterfactual signal is gold for training.

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your agent

```bash
cp .env.example .env
# Edit .env with your Pinata JWT and agent details
```

### 3. Instrument your bot

Drop the logger into your bot:

```python
from reppo_sdk import PodLogger

logger = PodLogger(agent_id="your-agent-id", agent_name="MyBot")

# Log an executed trade
logger.log_trade(
    pair="BTC",
    side="long",
    entry_price=84500.0,
    size_usd=150.0,
    leverage=5,
    signals={"rsi_1h": 28.4, "obi": 0.61, "reasons": ["RSI oversold", "OBI buy"]},
    score=6.2,
    strategy="swing"
)

# Log a near-miss (signal evaluated but not taken)
logger.log_near_miss(
    pair="ETH",
    side="long",
    score=4.8,
    threshold=5.5,
    signals={"rsi_1h": 35.1, "reasons": ["RSI mild", "EMA mixed"]},
    reason_not_traded="score_4.8_below_threshold_5.5"
)

# Log a trade close
logger.log_close(
    pair="BTC",
    exit_price=85200.0,
    pnl_pct=0.0083,
    hold_hours=6.4,
    close_reason="take_profit"
)
```

### 4. Build and pin pods

```bash
# Build pods for the last 48h epoch and pin to IPFS
python3 build_pods.py

# Dry run (preview without pinning)
python3 build_pods.py --dry-run

# Check buffer status
python3 build_pods.py --status
```

### 5. Set up the cron

```bash
# Add to crontab — runs every 6 hours
0 */6 * * * cd /path/to/reppo-tradinggymai-datanet-pipeline && python3 build_pods.py >> /tmp/pod_builder.log 2>&1
```

---

## Project Structure

```
reppo-tradinggymai-datanet-pipeline/
├── build_pods.py          # Main pod builder — run this every epoch
├── build_t4_pods.py       # Deep strategy refinement (T4) builder
├── reppo_sdk/
│   ├── __init__.py
│   ├── logger.py          # PodLogger — drop into your bot
│   ├── builder.py         # Pod construction + IPFS pinning
│   └── utils.py           # Watermarking, dedup, schema validation
├── schemas/
│   ├── t1_trade.json      # T1 record schema
│   ├── t2_near_miss.json  # T2 record schema
│   ├── t3_scan.json       # T3 record schema
│   └── t4_refinement.json # T4 pod schema
├── examples/
│   ├── basic_bot.py       # Minimal bot with logging wired in
│   └── hyperliquid_bot.py # Hyperliquid-specific example
├── docs/
│   ├── SCHEMA.md          # Full pod schema reference
│   ├── REPPO.md           # How Reppo rewards work
│   └── CONTRIBUTING.md    # How to contribute data to the datanet
├── .env.example
├── requirements.txt
└── README.md
```

---

## Real-World Example

This pipeline is live and running on two agents in the [Virtuals DegenClaw $100K weekly competition](https://degen.virtuals.io):

- **hottubleeee** (Agent 565) — scalp/sniper strategy
- **HotBot** (Agent 702) — swing strategy, 16-24h holds

Both run long-only with a patience exit protocol. Their pods are pinned to IPFS every 6 hours and submitted to the TradingGym AI datanet.

You can verify their on-chain activity on Hyperliquid:
- hottubleeee: `0x322bc1b25ade46238fc2bc9c34623ac6aed6b83a`

---

## Why contribute data?

- **Reppo rewards** — earn from the datanet for high-quality submissions
- **Verifiable track record** — your data is on IPFS, permanently timestamped
- **Better models** — contribute to AI that learns from real autonomous trading
- **Reputation** — build a public, auditable record of your bot's performance

---

## Contributing

PRs welcome. If you're running a bot and want to contribute data to the network, open an issue — happy to help you get wired up.

---

## License

MIT — use it, fork it, build on it.

---

*Built on [Reppo](https://reppo.ai) × [TradingGym AI](https://tradinggym.ai) × [Virtuals Protocol](https://virtuals.io)*
