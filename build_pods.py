#!/usr/bin/env python3
"""
build_pods.py — Build and pin epoch pods to IPFS for Reppo submission.

Usage:
    python3 build_pods.py                  # build last 48h epoch
    python3 build_pods.py --hours 96       # build last 96h (2 epochs)
    python3 build_pods.py --dry-run        # preview without pinning
    python3 build_pods.py --status         # show buffer counts only
    python3 build_pods.py --keep-buffers   # build + pin but don't clear
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from reppo_sdk import PodLogger, build_pods

AGENT_NAME = os.getenv("AGENT_NAME", "MyBot")
AGENT_ID   = os.getenv("AGENT_ID", "unknown")
PINATA_JWT = os.getenv("PINATA_JWT", "")
DATA_DIR   = Path(os.getenv("DATA_DIR", f"./data/{AGENT_NAME}"))


def main():
    parser = argparse.ArgumentParser(description="Build and pin Reppo epoch pods")
    parser.add_argument("--hours",        type=int,  default=48,    help="Hours to include in this epoch (default: 48)")
    parser.add_argument("--dry-run",      action="store_true",       help="Preview without pinning to IPFS")
    parser.add_argument("--status",       action="store_true",       help="Show buffer counts and exit")
    parser.add_argument("--keep-buffers", action="store_true",       help="Don't clear buffers after build")
    args = parser.parse_args()

    if args.status:
        logger = PodLogger(agent_id=AGENT_ID, agent_name=AGENT_NAME, data_dir=DATA_DIR)
        counts = logger.buffer_counts()
        print(f"\n📊 Buffer status for {AGENT_NAME}:")
        print(f"   T1 (executed trades): {counts['t1_trades']} records")
        print(f"   T2 (near-misses):     {counts['t2_near_misses']} records")
        print(f"   T3 (scan cycles):     {counts['t3_scans']} records")
        return

    if not PINATA_JWT and not args.dry_run:
        print("❌ PINATA_JWT not set in .env — run with --dry-run or add your JWT")
        sys.exit(1)

    results = build_pods(
        agent_name=AGENT_NAME,
        agent_id=AGENT_ID,
        data_dir=DATA_DIR,
        pinata_jwt=PINATA_JWT,
        hours=args.hours,
        dry_run=args.dry_run,
        clear_after=not args.keep_buffers,
    )

    print("\n────────────────────────────────────────────")
    print("📌 Submit these CIDs to Reppo:")
    for pod_num, cid in results.items():
        label = {1: "T1 Trades", 2: "T2 Near-misses", 3: "T3 Scans", 4: "T4 Refinement"}[pod_num]
        print(f"   Pod {pod_num} ({label}): {cid}")
        if cid and not args.dry_run:
            print(f"      https://ipfs.io/ipfs/{cid}")
    print("────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
