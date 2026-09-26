from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
if TYPE_CHECKING:
    from hftengine.engine.simulator import BacktestResult

def fee_tick_impact(notional: float, tick_size: float, price: float, maker_fee_bps: float = 2.0, rebate_bps: float = 0.5) -> dict:
    tick_bps = (tick_size / price) * 1e4 if price > 0 else float("inf")
    return {"tick_bps": tick_bps, "fee_usd": notional * maker_fee_bps / 1e4, "rebate_usd": notional * rebate_bps / 1e4, "fee_in_ticks": maker_fee_bps / tick_bps if tick_bps else float("inf"), "rebate_in_ticks": rebate_bps / tick_bps if tick_bps else float("inf")}

def session_report(result: "BacktestResult", price: float = 60000.0, tick: float = 0.1) -> dict:
    s = result.summary()
    econ = fee_tick_impact(s["notional"], tick, price)
    lat = np.array(result.latencies_ms, dtype=float) if result.latencies_ms else np.array([])
    return {**s, "economics": econ, "latency": {"p50": float(np.percentile(lat, 50)) if lat.size else 0.0, "p99": float(np.percentile(lat, 99)) if lat.size else 0.0, "mean": float(lat.mean()) if lat.size else 0.0}, "reject_rate": s["rejected"] / max(1, s["n_frames"])}
