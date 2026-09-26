"""HFTENGINE improved — market-making backtest + replay metrics."""

from .engine.book import OrderBook
from .engine.simulator import BacktestEngine, BacktestResult
from .strategy.grid import GridMarketMaker
from .metrics.session import session_report

__version__ = "0.3.0"
__all__ = ["OrderBook", "BacktestEngine", "BacktestResult", "GridMarketMaker", "session_report"]
