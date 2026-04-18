"""
Pod builder — reads T1/T2/T3 buffers, constructs structured pods, pins to IPFS via Pinata.
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


def _ts_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_buffer(path: Path, since: datetime | None = None) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            if since:
                ts_str = r.get("ts", "")
                if ts_str and ts_str < since.isoformat():
                    continue
            records.append(r)
        except json.JSONDecodeError:
            continue
    return records


def pin_to_ipfs(data: dict, name: str, pinata_jwt: str, dry_run: bool = False) -> Optional[str]:
    """
    Pin a JSON object to IPFS via Pinata.
    Returns the IPFS CID, or None on failure.
    """
    if dry_run:
        print(f"  [DRY RUN] Would pin: {name} ({len(json.dumps(data))} bytes)")
        return f"dry-run-cid-{name}"

    payload = {
        "pinataContent": data,
        "pinataMetadata": {"name": name},
        "pinataOptions": {"cidVersion": 1},
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {pinata_jwt}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result.get("IpfsHash")
    except Exception as e:
        print(f"  ⚠️  Pinata error for {name}: {e}")
        return None


def build_pods(
    agent_name: str,
    agent_id: str,
    data_dir: Path,
    pinata_jwt: str,
    hours: int = 48,
    dry_run: bool = False,
    clear_after: bool = True,
) -> dict:
    """
    Build all 4 pods from buffered data and pin to IPFS.
    Returns dict of {pod_num: cid}.
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=hours)
    epoch_id = now.strftime("%Y%m%d-%H%M")

    t1_path = data_dir / "tier1_buffer.jsonl"
    t2_path = data_dir / "tier2_buffer.jsonl"
    t3_path = data_dir / "tier3_buffer.jsonl"

    t1 = _load_buffer(t1_path, since)
    t2 = _load_buffer(t2_path, since)
    t3 = _load_buffer(t3_path, since)

    print(f"\n📦 Building epoch {epoch_id} | T1={len(t1)} trades | T2={len(t2)} near-misses | T3={len(t3)} scans")

    meta = {
        "agent": agent_name,
        "agent_id": agent_id,
        "epoch_id": epoch_id,
        "built_at": _ts_now(),
        "hours": hours,
        "data_schema": "reppo-pod-v1.0",
    }

    results = {}

    # ── Pod 1: Executed Trades (T1) ──────────────────────────────────────────
    opens  = [r for r in t1 if r.get("type") == "open"]
    closes = [r for r in t1 if r.get("type") == "close"]
    wins   = [r for r in closes if (r.get("pnl_pct") or 0) > 0]
    losses = [r for r in closes if (r.get("pnl_pct") or 0) <= 0]
    win_rate = len(wins) / len(closes) if closes else None

    pod1 = {
        **meta,
        "pod_type": "tier1_executed_trades",
        "summary": {
            "total_opens": len(opens),
            "total_closes": len(closes),
            "win_rate": round(win_rate, 4) if win_rate is not None else None,
            "avg_pnl_pct": round(sum(r.get("pnl_pct",0) for r in closes) / len(closes), 4) if closes else None,
        },
        "trades": t1,
    }
    cid1 = pin_to_ipfs(pod1, f"{agent_name}-{epoch_id}-pod1-trades", pinata_jwt, dry_run)
    results[1] = cid1
    print(f"  📌 Pod 1 (Trades): {cid1}")

    # ── Pod 2: Near-Misses (T2) ───────────────────────────────────────────────
    pod2 = {
        **meta,
        "pod_type": "tier2_close_calls",
        "summary": {
            "total_near_misses": len(t2),
            "avg_score": round(sum(r.get("score",0) for r in t2) / len(t2), 2) if t2 else None,
        },
        "near_misses": t2,
    }
    cid2 = pin_to_ipfs(pod2, f"{agent_name}-{epoch_id}-pod2-near-misses", pinata_jwt, dry_run)
    results[2] = cid2
    print(f"  📌 Pod 2 (Near-misses): {cid2}")

    # ── Pod 3: Scan Coverage (T3) ─────────────────────────────────────────────
    pod3 = {
        **meta,
        "pod_type": "tier3_scan_coverage",
        "summary": {
            "total_scan_cycles": len(t3),
            "unique_pairs": list(set(p for r in t3 for p in r.get("pairs_scanned", []))),
        },
        "scans": t3,
    }
    cid3 = pin_to_ipfs(pod3, f"{agent_name}-{epoch_id}-pod3-scans", pinata_jwt, dry_run)
    results[3] = cid3
    print(f"  📌 Pod 3 (Scans): {cid3}")

    # ── Pod 4: Strategy Refinement (T4) ───────────────────────────────────────
    loss_patterns = _extract_loss_patterns(closes)
    recommendations = _generate_recommendations(t1, t2)

    pod4 = {
        **meta,
        "pod_type": "tier4_strategy_refinement",
        "summary": {
            "trades_analyzed": len(closes),
            "near_misses_analyzed": len(t2),
            "loss_patterns": len(loss_patterns),
            "recommendations": len(recommendations),
        },
        "loss_patterns": loss_patterns,
        "near_miss_analysis": _analyze_near_misses(t2),
        "recommendations": recommendations,
    }
    cid4 = pin_to_ipfs(pod4, f"{agent_name}-{epoch_id}-pod4-refinement", pinata_jwt, dry_run)
    results[4] = cid4
    print(f"  📌 Pod 4 (Refinement): {cid4}")

    # ── Clear buffers if all pods pinned ─────────────────────────────────────
    all_pinned = all(v for v in results.values())
    if clear_after and all_pinned and not dry_run:
        for path in [t1_path, t2_path, t3_path]:
            if path.exists():
                path.write_text("")
        print(f"  🗑️  Buffers cleared — ready for next epoch")
    elif not all_pinned:
        print(f"  ⚠️  One or more pods failed to pin — buffers NOT cleared")

    print(f"\n✅ Epoch {epoch_id} complete\n")
    return results


def _extract_loss_patterns(closes: list[dict]) -> list[dict]:
    losses = [r for r in closes if (r.get("pnl_pct") or 0) < 0]
    patterns = {}
    for trade in losses:
        for reason in trade.get("signals", {}).get("reasons", []):
            patterns[reason] = patterns.get(reason, 0) + 1
    return [{"pattern": k, "occurrences": v} for k, v in sorted(patterns.items(), key=lambda x: -x[1])]


def _analyze_near_misses(t2: list[dict]) -> dict:
    if not t2:
        return {}
    scores = [r.get("score", 0) for r in t2]
    pairs = {}
    for r in t2:
        p = r.get("pair", "?")
        pairs[p] = pairs.get(p, 0) + 1
    return {
        "total": len(t2),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores),
        "top_pairs": sorted(pairs.items(), key=lambda x: -x[1])[:5],
    }


def _generate_recommendations(t1: list[dict], t2: list[dict]) -> list[str]:
    recs = []
    closes = [r for r in t1 if r.get("type") == "close"]
    wins = [r for r in closes if (r.get("pnl_pct") or 0) > 0]
    if closes and len(wins) / len(closes) < 0.4:
        recs.append("Win rate below 40% — consider raising signal threshold")
    high_near_misses = [r for r in t2 if r.get("score", 0) >= 5.0]
    if len(high_near_misses) > 50:
        recs.append(f"{len(high_near_misses)} near-misses scored ≥5.0 — consider lowering threshold slightly")
    return recs
