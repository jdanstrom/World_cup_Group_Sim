"""Team, Match, and Group dataclasses for the 2026 World Cup simulator."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class Team:
    name: str
    code: str
    group: str
    pot: int
    confederation: str
    is_host: bool
    elo: float

    def __hash__(self) -> int:
        return hash(self.code)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Team) and self.code == other.code


@dataclass
class MatchResult:
    home: Team
    away: Team
    home_goals: int
    away_goals: int

    @property
    def winner(self) -> Optional[Team]:
        if self.home_goals > self.away_goals:
            return self.home
        if self.away_goals > self.home_goals:
            return self.away
        return None

    @property
    def is_draw(self) -> bool:
        return self.home_goals == self.away_goals

    def points(self, team: Team) -> int:
        if self.is_draw:
            return 1
        return 3 if self.winner == team else 0

    def gf(self, team: Team) -> int:
        return self.home_goals if team == self.home else self.away_goals

    def ga(self, team: Team) -> int:
        return self.away_goals if team == self.home else self.home_goals


@dataclass
class GroupStanding:
    team: Team
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    gf: int = 0
    ga: int = 0

    @property
    def points(self) -> int:
        return self.wins * 3 + self.draws

    @property
    def gd(self) -> int:
        return self.gf - self.ga

    def update(self, result: MatchResult) -> None:
        self.played += 1
        self.gf += result.gf(self.team)
        self.ga += result.ga(self.team)
        pts = result.points(self.team)
        if pts == 3:
            self.wins += 1
        elif pts == 1:
            self.draws += 1
        else:
            self.losses += 1


def load_teams(csv_path: Optional[Path] = None) -> dict[str, Team]:
    """Load teams.csv and return a dict keyed by team code."""
    if csv_path is None:
        csv_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "teams.csv"
    df = pd.read_csv(csv_path, comment="#")
    teams: dict[str, Team] = {}
    for _, row in df.iterrows():
        t = Team(
            name=row["team"],
            code=row["code"],
            group=row["group"],
            pot=int(row["pot"]),
            confederation=row["confederation"],
            is_host=bool(row["is_host"]),
            elo=float(row["elo"]),
        )
        teams[t.code] = t
    return teams


def teams_by_group(teams: dict[str, Team]) -> dict[str, list[Team]]:
    """Return teams grouped by their group letter."""
    groups: dict[str, list[Team]] = {}
    for t in teams.values():
        groups.setdefault(t.group, []).append(t)
    return groups
