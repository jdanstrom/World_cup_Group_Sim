"""Rank teams within a group and select the best 8 third-placed teams.

FIFA 2026 tiebreaker order (within a group):
  1. Points
  2. Goal difference
  3. Goals for
  4. (Head-to-head not implemented here — random draw used as final fallback)

Best third-placed selection:
  The 8 best third-placed teams from 12 groups advance. Ranking uses the
  same criteria: points, then GD, then GF.
"""
from __future__ import annotations

import random
from src.data_model import GroupStanding


def _sort_key(s: GroupStanding) -> tuple:
    return (s.points, s.gd, s.gf)


def rank_group(standings: list[GroupStanding]) -> list[GroupStanding]:
    """Return standings sorted 1st→4th. Ties broken randomly (final fallback)."""
    shuffled = standings[:]
    random.shuffle(shuffled)  # randomise before stable sort to handle ties fairly
    return sorted(shuffled, key=_sort_key, reverse=True)


def qualify_from_groups(
    all_group_standings: dict[str, list[GroupStanding]],
) -> tuple[list[GroupStanding], list[GroupStanding], list[GroupStanding]]:
    """Return (first_placed, second_placed, third_placed_qualifiers).

    Third-placed: the top 8 of the 12 third-placed teams advance.
    """
    first_placed: list[GroupStanding] = []
    second_placed: list[GroupStanding] = []
    third_placed_all: list[GroupStanding] = []

    for group_letter in sorted(all_group_standings):
        ranked = rank_group(all_group_standings[group_letter])
        first_placed.append(ranked[0])
        second_placed.append(ranked[1])
        third_placed_all.append(ranked[2])

    third_placed_all.sort(key=_sort_key, reverse=True)
    third_placed_qualifiers = third_placed_all[:8]

    return first_placed, second_placed, third_placed_qualifiers
