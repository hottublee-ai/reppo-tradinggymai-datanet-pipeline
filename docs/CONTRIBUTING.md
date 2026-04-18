# Contributing to the TradingGym AI Datanet

## Who should contribute?

Anyone running an autonomous trading bot — whether it's:
- A signal bot on Hyperliquid, Binance, dYdX, or any perps exchange
- A prediction market bot on Polymarket or Kalshi  
- A spot trading bot on any DEX or CEX
- A paper trading / backtesting agent

Your data is valuable regardless of win rate. Near-misses (T2) are often *more* valuable than actual trades because they capture the decision boundary.

---

## What makes good pod data?

**High quality:**
- Full signal context in every record (not just entry price + outcome)
- Honest near-misses — log signals you evaluated, not just ones you took
- Consistent schema across epochs
- Regular cadence — publish when your data is ready; more frequent is better but there's no forced schedule

**Low quality (still accepted, lower reward):**
- Price + outcome only, no signal context
- Irregular or sparse submissions
- Single-asset bots with very few trades

---

## How to get started

1. Fork this repo
2. Drop `PodLogger` into your bot (5 minutes)
3. Get a free Pinata account at [pinata.cloud](https://pinata.cloud)
4. Run `build_pods.py` whenever you're ready — manually or via cron, on whatever schedule suits you
5. When your pods are built and pinned, publish them to the [TradingGym AI subnet on Reppo](https://reppo.ai/subnets/cmnhuowns000bic04e16t6735) (see `docs/REPPO.md` for the full publication flow)

> The pipeline never auto-submits. You build and pin pods locally, then publish them yourself when you're ready.

That's it. Your bot is now contributing to the datanet.

---

## Verifiability

The more verifiable your data, the more it's worth. Best practice:
- Include your on-chain address in `agent_meta`
- Include trade timestamps that can be cross-referenced on-chain
- Log the exchange and market for each trade

If your trades are on Hyperliquid, they're fully verifiable — anyone can check your address's trade history.

---

## Questions?

Open an issue or reach out on X: [@Hottubleed](https://x.com/Hottubleed)
