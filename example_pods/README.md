# Example Pods

Fully filled JSON examples for each pod tier. Use these as a reference when instrumenting your bot or debugging schema validation.

| File | Tier | What it shows |
|------|------|---------------|
| `t1_trade_example.json` | T1 — Executed Trades | An open + close record pair for a single BTC long |
| `t2_near_miss_example.json` | T2 — Near-Misses | Two signals that were evaluated but not traded, with different rejection reasons |
| `t3_scan_example.json` | T3 — Market Scans | Two scan cycles across 8 pairs with regime state and market notes |
| `t4_refinement_example.json` | T4 — Strategy Refinement | A full epoch refinement pod with loss patterns, near-miss analysis, and recommendations |

For the full schema reference, see [`docs/SCHEMA.md`](../docs/SCHEMA.md).

**Required vs optional fields:** Each schema file in `schemas/` lists which fields are `required`. Everything else is optional but improves reward potential — include as much signal context as you can.
