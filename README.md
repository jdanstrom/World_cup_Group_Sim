# 2026 World Cup Group Stage Simulator

A Monte Carlo simulator for the 48-team 2026 FIFA World Cup group stage,
using Elo ratings to drive a bivariate Poisson match model.

## Project structure

```
wc2026-sim/
├── data/
│   ├── raw/              # raw scrapes (empty for now)
│   └── processed/
│       └── teams.csv     # 48 teams + group + pot + confederation + Elo
├── src/
│   ├── validate_teams.py # sanity checks on teams.csv
│   ├── scrape_elo.py     # stub for refreshing Elo ratings
│   ├── data_model.py     # (next) Team / Match / Group dataclasses
│   ├── match_engine.py   # (next) single-match Poisson simulator
│   ├── group_stage.py    # (next) plays all 6 matches in a group
│   ├── standings.py      # (next) ranks teams + picks best 8 third-placed
│   └── monte_carlo.py    # (next) N-simulation wrapper + aggregation
├── notebooks/
├── tests/
└── requirements.txt
```

## Current status

**Step 1 complete:** teams dataset built and validated.

All 48 teams from the Dec 2025 draw are loaded, including the six
playoff winners (Bosnia, Sweden, Turkey, Czechia from UEFA; Iraq and
DR Congo from the intercontinental playoff).

Elo ratings are currently manual, flagged in `elo_source` as
`manual_april_2026`. The `scrape_elo.py` stub documents how to
refresh them.

## Next steps

2. Match engine (single-match Poisson simulator)
3. Group stage logic (6 matches per group)
4. Standings + tiebreakers (including best-8-of-12 third-placed teams)
5. Monte Carlo wrapper
6. Visualization
