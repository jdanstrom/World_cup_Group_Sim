"""Monte Carlo wrapper: run N full group-stage simulations and aggregate results."""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd
from numpy.random import default_rng

from src.data_model import load_teams, teams_by_group
from src.group_stage import play_group
from src.standings import qualify_from_groups


def run(n: int = 10_000, seed: int | None = None) -> pd.DataFrame:
    """Run N simulations of the group stage.

    Returns a DataFrame with one row per team containing:
      - team, code, group, elo
      - finish_1st, finish_2nd, finish_3rd, finish_4th  (counts)
      - qualified  (count of times the team advanced — 1st, 2nd, or best 3rd)
      - qualify_pct, finish_1st_pct, finish_2nd_pct, finish_3rd_pct, finish_4th_pct
    """
    rng = default_rng(seed)
    teams = load_teams()
    groups = teams_by_group(teams)

    finish_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    qualified_count: dict[str, int] = defaultdict(int)

    for _ in range(n):
        all_group_standings = {
            letter: play_group(group_teams, rng)
            for letter, group_teams in groups.items()
        }
        first, second, third_qual = qualify_from_groups(all_group_standings)

        qualified_codes = {s.team.code for s in first + second + third_qual}

        for letter, standings_list in all_group_standings.items():
            from src.standings import rank_group
            ranked = rank_group(standings_list)
            for pos, standing in enumerate(ranked):
                finish_counts[standing.team.code][pos] += 1
                if standing.team.code in qualified_codes:
                    qualified_count[standing.team.code] += 1

    rows = []
    for code, team in teams.items():
        counts = finish_counts[code]
        rows.append({
            "team": team.name,
            "code": code,
            "group": team.group,
            "elo": team.elo,
            "finish_1st": counts[0],
            "finish_2nd": counts[1],
            "finish_3rd": counts[2],
            "finish_4th": counts[3],
            "qualified": qualified_count[code],
            "qualify_pct": round(100 * qualified_count[code] / n, 1),
            "finish_1st_pct": round(100 * counts[0] / n, 1),
            "finish_2nd_pct": round(100 * counts[1] / n, 1),
            "finish_3rd_pct": round(100 * counts[2] / n, 1),
            "finish_4th_pct": round(100 * counts[3] / n, 1),
        })

    df = pd.DataFrame(rows).sort_values("qualify_pct", ascending=False).reset_index(drop=True)
    return df


if __name__ == "__main__":
    print("Running 10,000 simulations...")
    results = run(n=10_000, seed=42)
    pd.set_option("display.max_rows", 60)
    pd.set_option("display.width", 120)
    print(results[["team", "group", "elo", "qualify_pct", "finish_1st_pct", "finish_2nd_pct", "finish_3rd_pct", "finish_4th_pct"]].to_string(index=False))
