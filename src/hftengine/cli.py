"""CLI: run synthetic session and print report."""
from __future__ import annotations
import argparse, json
from hftengine.engine.simulator import BacktestEngine
from hftengine.strategy.grid import GridMarketMaker
from hftengine.metrics.session import session_report

def main() -> None:
    ap = argparse.ArgumentParser(prog="hftengine")
    ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--grid-num", type=int, default=5)
    ap.add_argument("--order-qty", type=float, default=0.002)
    ap.add_argument("--feed-latency-ms", type=float, default=50.0)
    ap.add_argument("--order-latency-ms", type=float, default=50.0)
    ap.add_argument("--fee-bps", type=float, default=2.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    strat = GridMarketMaker(grid_num=a.grid_num, order_qty=a.order_qty)
    eng = BacktestEngine(feed_latency_ms=a.feed_latency_ms, order_latency_ms=a.order_latency_ms, maker_fee_bps=a.fee_bps, strategy=strat)
    result = eng.run_synthetic(n_steps=a.steps, seed=a.seed)
    report = session_report(result)
    print(json.dumps(report, indent=2) if a.json else report)

if __name__ == "__main__":
    main()
