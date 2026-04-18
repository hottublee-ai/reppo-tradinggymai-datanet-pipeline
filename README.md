# 🧠 TradingGym AI — Reppo Pod Pipeline

**The data pipeline behind the TradingGym AI datanet. Instrument your bot. Contribute verifiable trading data. Earn Reppo rewards.**

Built by [@Hottubleed](https://x.com/Hottubleed) — and running live on two agents in the [Virtuals DegenClaw $100K weekly competition](https://degen.virtuals.io).

---

## Why this exists

The [TradingGym AI datanet](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735) is a shared corpus of real autonomous trading behavior — entries, exits, near-misses, market scans, and strategy refinements. It's what trains better AI trading models.

Right now, most trading bots generate this data and throw it away.

This pipeline captures it, structures it into verifiable IPFS pods, and submits it to the [TradingGym AI subnet on Reppo](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735) — where you earn rewards for quality contributions.

**Your bot is already generating the data. This pipeline just makes it count.**

---

## How the datanet works

Every contributor runs this pipeline alongside their bot. When you're ready, you generate up to 4 pods:

| Pod | Tier | What it captures |
|-----|------|-----------------|
| Pod 1 | T1 — Executed Trades | Every real entry + exit, with full signal rationale |
| Pod 2 | T2 — Near-Misses | Signals evaluated but not traded (often the most valuable) |
| Pod 3 | T3 — Scan Coverage | All markets × scan cycles + macro regime state |
| Pod 4 | T4 — Strategy Refinement | Loss patterns, win attribution, auto-generated recommendations |

These pods are pinned to IPFS via Pinata and submitted to Reppo. The data is permanent, verifiable, and auditable on-chain.

> **Why near-misses?** T2 data captures your bot's decision boundary — what it *almost* traded and why it didn't. That counterfactual signal is extremely rare and highly valuable for training. Most bots never log it. This pipeline does.

---

## What you need

- A trading bot (any exchange, any language — Python wrapper included)
- A free [Pinata](https://pinata.cloud) account for IPFS pinning
- A wallet to submit CIDs to the [TradingGym AI subnet on Reppo](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735) and earn rewards

**Cost: free. Setup: ~15 minutes.**

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/hottublee-ai/reppo-tradinggymai-datanet-pipeline.git
cd reppo-tradinggymai-datanet-pipeline
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```env
PINATA_JWT=your_pinata_jwt_here      # from pinata.cloud — free tier is enough
AGENT_NAME=MyBot                     # your bot's name
AGENT_ID=your_agent_id               # your ID on degen.virtuals.io, or any unique string
```

### 3. Add 3 logging calls to your bot

```python
from reppo_sdk import PodLogger

logger = PodLogger(agent_id="your-agent-id", agent_name="MyBot")

# When you open a trade:
logger.log_trade(
    pair="BTC", side="long", entry_price=84500.0, size_usd=150.0, leverage=5,
    signals={"rsi_1h": 28.4, "obi": 0.61, "reasons": ["RSI oversold", "OBI buy"]},
    score=6.2, strategy="swing"
)

# When a signal scores but you don't trade it (near-miss):
logger.log_near_miss(
    pair="ETH", side="long", score=4.8, threshold=5.5,
    signals={"rsi_1h": 35.1, "reasons": ["RSI mild", "EMA mixed"]},
    reason_not_traded="score_4.8_below_threshold_5.5"
)

# When you close a trade:
logger.log_close(
    pair="BTC", exit_price=85200.0, pnl_pct=0.0083,
    hold_hours=6.4, close_reason="take_profit"
)
```

That's the full integration. Three calls. No bot rewrite required.

### 4. Build and pin pods on your schedule

Run `build_pods.py` whenever you're ready. It builds from your accumulated data — no fixed schedule required.

```bash
# Build from the last 48h of data (default) and pin to IPFS
python3 build_pods.py

# Preview without pinning
python3 build_pods.py --dry-run

# Check how much data you've accumulated
python3 build_pods.py --status
```

### 5. Automate with cron (optional)

If you want a regular automated cadence, add a cron entry. Otherwise just run `build_pods.py` manually when you want to publish.

```bash
# Example: run daily at midnight
0 0 * * * cd /path/to/reppo-tradinggymai-datanet-pipeline && python3 build_pods.py >> /tmp/pod_builder.log 2>&1
```

### 6. Submit your CIDs to Reppo (manual step)

After each build, you'll see output like:

```
────────────────────────────────────────────
📌 Your pod CIDs are ready to submit:
   Pod 1 (T1 Trades):        bafybeig...
   Pod 2 (T2 Near-misses):   bafybeih...
   Pod 3 (T3 Scans):         bafybeii...
   Pod 4 (T4 Refinement):    bafybeij...
────────────────────────────────────────────
```

**This step is manual — you publish your own pods.** Go to the [TradingGym AI subnet on Reppo](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735), connect your wallet, and fill in the publication form for each pod. About 5 minutes of work whenever you're ready to publish. See [`docs/REPPO.md`](docs/REPPO.md) for the full two-step publication flow (pin → register).

> **Note:** The pipeline never auto-submits to Reppo. Your pods are yours — you decide when and what to publish.

See [`docs/REPPO.md`](docs/REPPO.md) for the full submission walkthrough and reward breakdown.

---

## Cost vs. benefit

| | What it takes | What you get |
|---|---|---|
| **Setup** | ~15 minutes | Drop-in logger, no bot rewrite |
| **Running cost** | Free (Pinata free tier) | IPFS pinning + datanet contribution |
| **Ongoing effort** | 5 min/epoch to manually submit CIDs | Automatic data capture, zero maintenance |
| **Upside** | Reppo rewards for quality data | Verifiable on-chain performance record |

---

## 🎥 Quick Setup (video coming soon)

A 60-second walkthrough: paste the logger, run `build_pods.py --status`, watch the buffers fill up, submit your first epoch.

*Want early access? DM [@Hottubleed](https://x.com/Hottubleed) on X.*

---

## Live example

This pipeline is running right now on live agents competing in the Virtuals DegenClaw $100K competition. On-chain trade history is fully verifiable — anyone can cross-reference the pod data against Hyperliquid.

Want to list your bot here? Open a PR.

---

## Repo structure

```
reppo-tradinggymai-datanet-pipeline/
├── build_pods.py             # Main CLI — build + pin epoch pods
├── reppo_sdk/
│   ├── logger.py             # PodLogger — drop this into your bot
│   ├── builder.py            # Pod construction + IPFS pinning
│   └── __init__.py
├── schemas/
│   ├── t1_trade.json         # T1 record schema
│   ├── t2_near_miss.json     # T2 record schema
│   ├── t3_scan.json          # T3 record schema
│   └── t4_refinement.json    # T4 pod schema
├── examples/
│   ├── basic_bot.py          # Minimal bot skeleton with logging
│   └── hyperliquid_bot.py    # Full Hyperliquid perps example
├── docs/
│   ├── REPPO.md              # Reppo submission guide + reward breakdown
│   ├── SCHEMA.md             # Full pod schema reference
│   └── CONTRIBUTING.md       # How to contribute to the datanet
├── .env.example
├── requirements.txt
└── README.md
```

---

## Works with any bot

The `PodLogger` writes flat JSONL files. Exchange-agnostic, language-agnostic (Python wrapper, raw schema works with anything). See:

- [`examples/basic_bot.py`](examples/basic_bot.py) — minimal skeleton, any exchange
- [`examples/hyperliquid_bot.py`](examples/hyperliquid_bot.py) — full Hyperliquid perps example
- [`schemas/`](schemas/) — raw JSON schemas if you want to implement in another language

---

## Contributing

PRs welcome. If you're running a bot and want to plug into the datanet, open an issue — happy to help you get wired up.

---

## License

MIT — use it, fork it, build on it.

---

*Built on [Reppo](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735) × [Virtuals Protocol](https://virtuals.io)*
