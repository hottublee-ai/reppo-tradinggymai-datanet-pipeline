# How Reppo Works — and How to Earn

## What is Reppo?

[Reppo](https://reppo.ai) is a decentralized AI training data marketplace. The [TradingGym AI subnet](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735) pays contributors for high-quality, verifiable trading data — because that data is used to train better autonomous trading models.

Your bot is generating this data right now. Most traders throw it away. With this pipeline, you capture it, structure it, and earn from it.

---

## The TradingGym AI Datanet

The datanet is a shared, on-chain record of autonomous trading agent behavior. Every pod you publish becomes part of the training corpus for the next generation of trading models.

Live subnet: **[reppo.ai/subnets/cmnhuowns000bic04e16t6735](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735)**

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

## How to Submit Your CIDs to Reppo

> **Pod submission is always manual — you publish your own pods. The pipeline never auto-submits on your behalf.**

After `build_pods.py` runs, it prints your CIDs:

```
────────────────────────────────────────────
📌 Your pod CIDs are ready to submit:
   Pod 1 (T1 Trades):        bafybeig...
   Pod 2 (T2 Near-misses):   bafybeih...
   Pod 3 (T3 Scans):         bafybeii...
   Pod 4 (T4 Refinement):    bafybeij...
────────────────────────────────────────────
```

**Submission steps:**

1. Go to the [TradingGym AI subnet on Reppo](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735) and connect your wallet
2. For each pod type, provide:
   - **Title** — e.g., "T1 Trades Epoch 2026-04-18"
   - **Description** — brief summary of what's in this pod (required)
   - **CID** — your IPFS content identifier in HTTPS format, e.g., `https://ipfs.io/ipfs/bafybeig...` (required)
   - **Image** — optional but recommended: a thumbnail/logo for your pod
3. Submit — your contribution is recorded on-chain

**CID format:** The CID must be a valid IPFS HTTP gateway URL. When `build_pods.py` pins your pod, it returns a base CID (e.g., `bafybeig...`). Prepend `https://ipfs.io/ipfs/` to create the full URL:
```
https://ipfs.io/ipfs/bafybeigyour_cid_here
```

Reppo validates the pod schema and cross-references on-chain data where possible. If your trades are on Hyperliquid, they're fully verifiable.

---

## Setting Up Your Reppo Account

1. Go to the [TradingGym AI subnet](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735)
2. Connect a wallet (the one associated with your trading agent)
3. Register as a data contributor
4. Build your first epoch pod with `build_pods.py`, then submit your CIDs

If you're competing on [Virtuals DegenClaw](https://degen.virtuals.io), your agent wallet is already the right one to use — your on-chain trade history is your verifiability proof.

> Your pods belong to you. The cron automates building and pinning to IPFS. You decide when to publish each epoch to the subnet.

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
