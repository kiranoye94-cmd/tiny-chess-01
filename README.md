# tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/kiranoye94-cmd/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard)
[![reward](https://make.fun/badge/tiny-chess-01/kiranoye94-cmd/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01)

A deterministic compact Python chess engine for the make.fun `tiny-chess-01` bounty. The committed `main.py` is a packed entrypoint produced by the official `makefun compress` command from a readable engine source; it uses only Python's standard library, calls no model, and communicates only with the contest environment.

## Run

The contest harness supplies `MAKEFUN_ENV_URL`:

```sh
python3 -P -s main.py
```
