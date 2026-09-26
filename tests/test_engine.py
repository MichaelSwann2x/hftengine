from hftengine import BacktestEngine, GridMarketMaker, session_report
from hftengine.engine.book import OrderBook

def test_book_queue():
    b = OrderBook(tick=0.1)
    b.apply_levels([(100.0, 5.0)], [(100.1, 5.0)])
    o = b.place("bid", 100.0, 1.0)
    assert o.ahead == 5.0
    assert b.queue_fraction(o.order_id) > 0

def test_backtest_runs():
    eng = BacktestEngine(strategy=GridMarketMaker(grid_num=3, order_qty=0.001))
    r = eng.run_synthetic(n_steps=100, seed=1)
    assert r.summary()["n_frames"] == 100
    assert "economics" in session_report(r)

def test_fill_path():
    eng = BacktestEngine()
    eng.seed_book(100.0)
    eng.strategy.on_book(eng.book)
    eng.step_trade(1.0, eng.book.best_ask()[0], 0.5, "buy")
    assert eng.result.frames
