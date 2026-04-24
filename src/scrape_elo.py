"""Refresh Elo ratings from eloratings.net.

Current state: STUB. The ratings in data/processed/teams.csv were entered
manually based on publicly reported April 2026 figures and are flagged with
elo_source = "manual_april_2026".

To refresh with live numbers:
  1. Download the current ratings table from https://www.eloratings.net/
     (the site renders its table via JavaScript, so either:
       - use a headless browser (Playwright/Selenium), OR
       - grab the JSON endpoint their front-end calls, OR
       - copy-paste the table manually into a CSV)
  2. Produce a two-column dataframe: team, elo
  3. Call update_teams_csv(new_ratings_df) below.

Kept as a stub because:
  - The site's ToS should be checked before automated scraping
  - 48 numbers is small enough to update by hand when it matters
  - Separating "where ratings come from" from "how we use them" keeps the
    rest of the pipeline stable
"""
from pathlib import Path
import pandas as pd

TEAMS_CSV = Path(__file__).resolve().parents[1] / "data" / "processed" / "teams.csv"


def update_teams_csv(new_ratings: pd.DataFrame, source_label: str) -> None:
    """Merge fresh Elo ratings into teams.csv.

    Args:
        new_ratings: DataFrame with columns ['team', 'elo'].
        source_label: Short string stored in elo_source, e.g. 'eloratings_2026_05_15'.
    """
    teams = pd.read_csv(TEAMS_CSV, comment="#")
    merged = teams.merge(new_ratings, on="team", how="left", suffixes=("_old", "_new"))

    missing = merged[merged["elo_new"].isna()]["team"].tolist()
    if missing:
        raise ValueError(f"No new Elo for: {missing}")

    merged["elo"] = merged["elo_new"].astype(int)
    merged["elo_source"] = source_label
    merged = merged.drop(columns=["elo_old", "elo_new"])
    merged.to_csv(TEAMS_CSV, index=False)
    print(f"Updated {len(merged)} teams, source={source_label}")


if __name__ == "__main__":
    print(__doc__)
