"""Event-driven backtest engine with latency and fee model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
from hftengine.engine.book import OrderBook
from hftengine.strategy.grid import GridMarketMaker

@dataclass
class Frame:
    t: float
    mid: Optional[float]
    spread: Optional[float]
    position: float
    n_open: int
    best_bid: Optional[float]
    best_ask: Optional[float]
    event: str

@dataclass
class BacktestResult:
    frames: List[Frame] = field(default_factory=list)
    fills: List[dict] = field(default_factory=list)
    latencies_ms: List[float] = field(default_factory=list)
    rejected: int = 0
    notional: float = 0.0
    pnl: float = 0.0
    fees: float = 0.0
    def summary(self) -> dict:
        return {"n_frames": len(self.frames), "n_fills": len(self.fills), "rejected": self.rejected, "notional": self.notional, "pnl": self.pnl, "fees": self.fees, "net": self.pnl - self.fees, "mean_latency_ms": float(np.mean(self.latencies_ms)) if self.latencies_ms else 0.0}

class BacktestEngine:
    def __init__(self, tick: float = 0.1, feed_latency_ms: float = 50.0, order_latency_ms: float = 50.0, maker_fee_bps: float = 2.0, strategy: Optional[GridMarketMaker] = None):
        self.book = OrderBook(tick=tick)
        self.strategy = strategy or GridMarketMaker()
        self.feed_latency_ms = feed_latency_ms
        self.order_latency_ms = order_latency_ms
        self.maker_fee_bps = maker_fee_bps
        self.result = BacktestResult()
        self._cash = 0.0

    def seed_book(self, mid: float, levels: int = 10, size: float = 1.0) -> None:
        tick = self.book.tick
        bids = [(mid - (i + 1) * tick, size * (1 + 0.1 * i)) for i in range(levels)]
        asks = [(mid + (i + 1) * tick, size * (1 + 0.1 * i)) for i in range(levels)]
        self.book.apply_levels(bids, asks)

    def step_trade(self, t: float, price: float, qty: float, aggressor: str) -> None:
        self.result.latencies_ms.append(self.feed_latency_ms + np.random.exponential(5.0))
        fills = self.book.on_trade(price, qty, aggressor)
        for o in fills:
            self.strategy.on_fill(o.side, o.qty)
            notional = o.qty * o.price
            fee = notional * (self.maker_fee_bps / 1e4)
            self.result.notional += notional
            self.result.fees += fee
            if o.side == "bid": self._cash -= notional
            else: self._cash += notional
            self.result.pnl = self._cash + self.strategy.position * price
            self.result.fills.append({"t": t, "side": o.side, "price": o.price, "qty": o.qty, "fee": fee})
        self.strategy.on_book(self.book)
        mid = self.book.mid()
        self.result.frames.append(Frame(t=t, mid=mid, spread=self.book.spread(), position=self.strategy.position, n_open=sum(1 for o in self.book.orders.values() if o.status == "open"), best_bid=self.book.best_bid()[0] if self.book.best_bid() else None, best_ask=self.book.best_ask()[0] if self.book.best_ask() else None, event="trade"))

    def run_synthetic(self, n_steps: int = 500, mid0: float = 60000.0, seed: int = 0) -> BacktestResult:
        rng = np.random.default_rng(seed)
        self.seed_book(mid0)
        self.strategy.on_book(self.book)
        mid = mid0
        t = 0.0
        for i in range(n_steps):
            t += float(rng.exponential(0.05))
            mid += float(rng.normal(0, 0.5))
            self.seed_book(mid, levels=8, size=float(rng.uniform(0.5, 2.0)))
            aggressor = "buy" if rng.random() > 0.5 else "sell"
            px = (self.book.best_ask() or (mid, 0))[0] if aggressor == "buy" else (self.book.best_bid() or (mid, 0))[0]
            qty = float(rng.uniform(0.001, 0.05))
            if self.order_latency_ms > 100 and rng.random() < 0.1:
                self.result.rejected += 1
            self.step_trade(t, px, qty, aggressor)
        return self.result
