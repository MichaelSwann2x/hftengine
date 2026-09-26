# HFTENGINE (improved full version)

Self-contained **market-making backtest + replay metrics** inspired by [mirkovicdev/HFTENGINE](https://github.com/mirkovicdev/HFTENGINE).

Fully working **without Rust/hftbacktest**: pure Python order book, grid strategy, latency/fee model, session reports.

## Install

```bash
pip install -e ".[dev]"
```

## Run

```bash
hftengine --steps 1000 --grid-num 5 --order-qty 0.002 --fee-bps 2.0 --json
```

## Library

```python
from hftengine import BacktestEngine, GridMarketMaker, session_report
eng = BacktestEngine(strategy=GridMarketMaker(grid_num=5), maker_fee_bps=2.0)
print(session_report(eng.run_synthetic(500)))
```

## Improvements

- Importable package + CLI + pytest
- Explicit queue-position model
- Fee vs tick economics + latency percentiles
- No Rust submodule required for core path

MIT. Attribution to mirkovicdev/HFTENGINE and hftbacktest tutorials.
