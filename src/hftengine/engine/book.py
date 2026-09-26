"""L2 order book with queue-position tracking for resting orders."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class RestingOrder:
    order_id: int
    side: str
    price: float
    qty: float
    ahead: float
    filled: float = 0.0
    status: str = "open"

@dataclass
class OrderBook:
    tick: float = 0.1
    bids: Dict[float, float] = field(default_factory=dict)
    asks: Dict[float, float] = field(default_factory=dict)
    orders: Dict[int, RestingOrder] = field(default_factory=dict)
    _next_id: int = 1

    def apply_levels(self, bids: List[Tuple[float, float]], asks: List[Tuple[float, float]]) -> None:
        self.bids = {float(p): float(s) for p, s in bids if float(s) > 0}
        self.asks = {float(p): float(s) for p, s in asks if float(s) > 0}

    def best_bid(self):
        if not self.bids: return None
        p = max(self.bids); return p, self.bids[p]

    def best_ask(self):
        if not self.asks: return None
        p = min(self.asks); return p, self.asks[p]

    def mid(self):
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None: return None
        return 0.5 * (bb[0] + ba[0])

    def spread(self):
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None: return None
        return ba[0] - bb[0]

    def place(self, side: str, price: float, qty: float) -> RestingOrder:
        book = self.bids if side == "bid" else self.asks
        ahead = float(book.get(price, 0.0))
        oid = self._next_id; self._next_id += 1
        order = RestingOrder(oid, side, price, qty, ahead=ahead)
        self.orders[oid] = order
        book[price] = ahead + qty
        return order

    def cancel(self, order_id: int) -> None:
        o = self.orders.get(order_id)
        if o is None or o.status != "open": return
        book = self.bids if o.side == "bid" else self.asks
        rem = o.qty - o.filled
        if o.price in book:
            book[o.price] = max(0.0, book[o.price] - rem)
            if book[o.price] <= 0: del book[o.price]
        o.status = "canceled"

    def on_trade(self, price: float, qty: float, aggressor: str):
        filled_orders = []
        side, book = ("ask", self.asks) if aggressor == "buy" else ("bid", self.bids)
        if price in book:
            take = min(book[price], qty)
            book[price] -= take
            if book[price] <= 1e-12: del book[price]
        for o in list(self.orders.values()):
            if o.status != "open" or o.side != side or abs(o.price - price) > 1e-12: continue
            if o.ahead > 0:
                dec = min(o.ahead, qty); o.ahead -= dec; traded_into_us = qty - dec
            else:
                traded_into_us = qty
            if traded_into_us > 0 and o.ahead <= 1e-12:
                fill = min(o.qty - o.filled, traded_into_us)
                o.filled += fill
                if o.filled + 1e-12 >= o.qty:
                    o.status = "filled"; filled_orders.append(o)
        return filled_orders

    def queue_fraction(self, order_id: int) -> float:
        o = self.orders.get(order_id)
        if o is None: return float("nan")
        book = self.bids if o.side == "bid" else self.asks
        level = book.get(o.price, o.ahead + (o.qty - o.filled))
        if level <= 0: return 0.0
        return float(o.ahead / level)

    def top_n(self, n: int = 10) -> dict:
        bids = sorted(self.bids.items(), key=lambda x: -x[0])[:n]
        asks = sorted(self.asks.items(), key=lambda x: x[0])[:n]
        return {"bids": bids, "asks": asks}
