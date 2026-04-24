"""Play all 6 round-robin matches in a single group."""
from __future__ import annotations

from itertools import combinations
from numpy.random import Generator

from src.data_model import GroupStanding, MatchResult, Team
from src.match_engine import simulate_match


def play_group(teams: list[Team], rng: Generator) -> list[GroupStanding]:
    """Simulate the round-robin for one group and return standings (unsorted)."""
    standings = {t.code: GroupStanding(team=t) for t in teams}

    for home, away in combinations(teams, 2):
        result = simulate_match(home, away, rng)
        standings[home.code].update(result)
        standings[away.code].update(result)

    return list(standings.values())
