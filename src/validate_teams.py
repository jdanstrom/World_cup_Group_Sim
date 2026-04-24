"""Quick sanity checks on teams.csv.

Confirms:
- 48 teams
- 12 groups (A-L), 4 teams each
- No duplicate teams
- Pots are 1-4 with exactly 12 teams each
- Three hosts flagged
- All required columns present
"""
import pandas as pd
from pathlib import Path

CSV = Path(__file__).resolve().parents[1] / "data" / "processed" / "teams.csv"


def load() -> pd.DataFrame:
    # '#' marks group-divider comments in the CSV -- pandas skips them
    return pd.read_csv(CSV, comment="#")


def main() -> None:
    df = load()
    print(f"Total teams: {len(df)}")
    assert len(df) == 48, "Expected 48 teams"

    groups = df.groupby("group").size()
    print("\nTeams per group:")
    print(groups.to_string())
    assert (groups == 4).all(), "Every group should have 4 teams"
    assert set(df["group"].unique()) == set("ABCDEFGHIJKL"), "Groups A-L required"

    pots = df.groupby("pot").size()
    print("\nTeams per pot:")
    print(pots.to_string())
    assert (pots == 12).all(), "Every pot should have 12 teams"

    hosts = df[df["is_host"]]["team"].tolist()
    print(f"\nHosts: {hosts}")
    assert set(hosts) == {"Canada", "Mexico", "United States"}, "3 hosts required"

    dupes = df[df.duplicated("team")]
    assert dupes.empty, f"Duplicate teams: {dupes['team'].tolist()}"

    print("\nElo summary:")
    print(df["elo"].describe().round(1).to_string())

    print("\nTop 5 by Elo:")
    print(df.nlargest(5, "elo")[["team", "group", "elo"]].to_string(index=False))
    print("\nBottom 5 by Elo:")
    print(df.nsmallest(5, "elo")[["team", "group", "elo"]].to_string(index=False))

    print("\nConfederation counts:")
    print(df.groupby("confederation").size().to_string())

    print("\nAll checks passed ✓")


if __name__ == "__main__":
    main()
