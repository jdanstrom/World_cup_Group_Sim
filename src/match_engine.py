"""Single-match simulator using a bivariate Poisson model driven by Elo ratings.

Elo → expected goal rates via Dixon-Coles-style scaling:
  - Elo difference maps to a win probability via the standard Elo formula.
  - That probability is converted into lambda_home / lambda_away such that
    the implied win probability from the Poisson model matches Elo.
  - A small home-advantage boost is applied when is_host is True.

The bivariate Poisson draws goals independently from Poisson(lambda_home)
and Poisson(lambda_away). This is the simplest valid model; Dixon-Coles
correlation corrections can be added later if calibration demands it.
"""
from __future__ import annotations

import math
import numpy as np
from numpy.random import Generator

from src.data_model import MatchResult, Team

# Average total goals per match at a neutral venue (calibrated to WC history)
MEAN_GOALS_PER_TEAM = 1.15

# Additive Elo boost for a hosting nation
HOME_ELO_BOOST = 100.0


def elo_win_prob(elo_a: float, elo_b: float) -> float:
    """Expected win probability for team A vs team B at a neutral venue."""
    return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / 400.0))


def _lambdas(home: Team, away: Team) -> tuple[float, float]:
    """Compute expected goals for each team."""
    home_elo = home.elo + (HOME_ELO_BOOST if home.is_host else 0.0)
    away_elo = away.elo

    p_home = elo_win_prob(home_elo, away_elo)
    p_away = elo_win_prob(away_elo, home_elo)

    # Scale lambdas so that E[home goals] / E[away goals] reflects the
    # relative strength, while the total stays near 2 * MEAN_GOALS_PER_TEAM.
    total = 2.0 * MEAN_GOALS_PER_TEAM
    lam_home = total * p_home / (p_home + p_away)
    lam_away = total * p_away / (p_home + p_away)
    return lam_home, lam_away


def simulate_match(home: Team, away: Team, rng: Generator) -> MatchResult:
    """Simulate a single match and return the result."""
    lam_home, lam_away = _lambdas(home, away)
    home_goals = int(rng.poisson(lam_home))
    away_goals = int(rng.poisson(lam_away))
    return MatchResult(home=home, away=away, home_goals=home_goals, away_goals=away_goals)


def expected_goals(home: Team, away: Team) -> tuple[float, float]:
    """Return (lambda_home, lambda_away) without sampling — useful for sanity checks."""
    return _lambdas(home, away)
