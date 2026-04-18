# How Reppo Works — and How to Earn

## What is Reppo?

[Reppo](https://reppo.ai) is a decentralized AI training data marketplace built on top of the [TradingGym AI](https://tradinggym.ai) datanet. It pays contributors for high-quality, verifiable trading data — because that data is used to train better autonomous trading models.

Your bot is generating this data right now. Most traders throw it away. With this pipeline, you capture it, structure it, and earn from it.

---

## The TradingGym AI Datanet

The datanet is a shared, on-chain record of autonomous trading agent behavior. Every pod you submit becomes part of the training corpus for the next generation of trading models.

**Who runs it?**  
The datanet is built and maintained by [@Hottubleed](https://x.com/Hottubleed) — with live bots already contributing data in the Virtuals Protocol $100K weekly competition.

This isn't a speculative project. The pipeline you're using is the exact same one running on live bots, submitting pods every epoch.

---

## How Rewards Work

Reppo rewards are based on **data quality and verifiability**, not just trade volume.

### Reward tiers (rough hierarchy)

| Data type | Reward potential | Why |
|-----------|-----------------|-----|
| T1 — Executed trades with full signal context | ⭐⭐⭐ | Verifiable on-chain, full rationale |
| T2 — Near-misses with signal context | ⭐⭐⭐⭐ | Counterfactual signal is rare and valuable |
| T3 — Scan coverage (regime + market state) | ⭐⭐ | Useful for macro regime modeling |
| T4 — Strategy refinement pods | ⭐⭐⭐ | Shows self-improvement loop |

**T2 (near-misses) is often the highest-value tier.** It captures what your bot *considered* and *rejected* — the decision boundary. That counterfactual signal is extremely valuable for training and hard to generate synthetically.

### What increases your reward

- Full signal context in every record (not just price + outcome)
- Regular cadence — 48h epochs submitted on schedule
- On-chain verifiability — your trades are cross-referenceable on Hyperliquid or another exchange
- Diverse coverage — multiple pairs, multiple regimes
- Consistent schema — records that validate against the pod schema

### What reduces your reward

- Price + outcome only, no signal context
- Irregular or sparse submissions
- Duplicate or fabricated records

---

## How to Submit CIDs to Reppo

After `build_pods.py` runs, it prints your CIDs:

```
────────────────────────────────────────────
📌 Submit these CIDs to Reppo:
   Pod 1 (T1 Trades):        bafybeig...
   Pod 2 (T2 Near-misses):   bafybeih...
   Pod 3 (T3 Scans):         bafybeii...
   Pod 4 (T4 Refinement):    bafybeij...
────────────────────────────────────────────
```

**Submission steps:**

1. Go to [reppo.ai](https://reppo.ai) and connect your wallet
2. Navigate to **Submit Data** → **Trading Pods**
3. Paste your CIDs (one per pod type)
4. Include your `agent_id` and epoch timestamp
5. Submit — your contribution is recorded on-chain

Reppo validates the pod schema and cross-references on-chain data where possible. If your trades are on Hyperliquid, they're fully verifiable.

---

## Setting Up Your Reppo Account

1. Go to [reppo.ai](https://reppo.ai)
2. Connect a wallet (the one associated with your trading agent)
3. Register as a data contributor
4. Start submitting epoch pods

If you're competing on [Virtuals DegenClaw](https://degen.virtuals.io), your agent wallet is already the right one to use — your on-chain trade history is your verifiability proof.

---

## Epoch Timing

Epochs are **48 hours**. The cron in this repo runs `build_pods.py` every 6 hours, but only submits when enough data has accumulated (configurable). Best practice:

- Let the bot run for at least 24h before your first epoch
- Build + pin every 48h
- Submit CIDs to Reppo within 24h of generating them

---

## Questions?

- Open an issue on this repo
- DM on X: [@Hottubleed](https://x.com/Hottubleed)
- Join the [Virtuals Protocol Discord](https://discord.gg/virtuals)
