"""Symmetric grid market-maker (hftbacktest tutorial style)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from hftengine.engine.book import OrderBook, RestingOrder

@dataclass
class GridMarketMaker:
    grid_num: int = 5
    order_qty: float = 0.002
    half_spread_ticks: int = 1
    grid_interval_ticks: int = 1
    max_position: float = 0.02
    position: float = 0.0
    open_bids: List[int] = field(default_factory=list)
    open_asks: List[int] = field(default_factory=list)

    def on_book(self, book: "OrderBook"):
        mid = book.mid(); bb, ba = book.best_bid(), book.best_ask()
        if mid is None or bb is None or ba is None: return []
        tick = book.tick; placed = []
        for oid in list(self.open_bids) + list(self.open_asks):
            o = book.orders.get(oid)
            if o is None or o.status != "open":
                if oid in self.open_bids: self.open_bids.remove(oid)
                if oid in self.open_asks: self.open_asks.remove(oid)
        bid_prices = [bb[0] - i * self.grid_interval_ticks * tick for i in range(self.grid_num)]
        ask_prices = [ba[0] + i * self.grid_interval_ticks * tick for i in range(self.grid_num)]
        if self.position < self.max_position and len(self.open_bids) < self.grid_num:
            for p in bid_prices:
                if any(book.orders[i].price == p and book.orders[i].status == "open" for i in self.open_bids if i in book.orders): continue
                if len(self.open_bids) >= self.grid_num: break
                o = book.place("bid", p, self.order_qty); self.open_bids.append(o.order_id); placed.append(o)
        if self.position > -self.max_position and len(self.open_asks) < self.grid_num:
            for p in ask_prices:
                if any(book.orders[i].price == p and book.orders[i].status == "open" for i in self.open_asks if i in book.orders): continue
                if len(self.open_asks) >= self.grid_num: break
                o = book.place("ask", p, self.order_qty); self.open_asks.append(o.order_id); placed.append(o)
        return placed

    def on_fill(self, side: str, qty: float) -> None:
        if side == "bid": self.position += qty
        else: self.position -= qty
