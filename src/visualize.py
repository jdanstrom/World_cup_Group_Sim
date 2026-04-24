"""Visualizations for Monte Carlo group-stage results.

Charts produced:
  1. qualify_by_group.png   — horizontal bar chart per group, teams sorted by qualify %
  2. finish_positions.png   — stacked bar (1st/2nd/3rd/4th %) for all 48 teams
  3. qualification_heatmap.png — heatmap: groups × finish position, cell = qualify %
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import seaborn as sns

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

POSITION_COLORS = {
    "1st": "#1a9641",
    "2nd": "#a6d96a",
    "3rd": "#fdae61",
    "4th": "#d7191c",
}

GROUP_LETTERS = list("ABCDEFGHIJKL")


# ---------------------------------------------------------------------------
# Chart 1 — Qualify % by group
# ---------------------------------------------------------------------------

def plot_qualify_by_group(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(3, 4, figsize=(18, 13))
    fig.suptitle("2026 World Cup — Group Stage Qualification Probability",
                 fontsize=16, fontweight="bold", y=1.01)

    for ax, letter in zip(axes.flat, GROUP_LETTERS):
        group_df = df[df["group"] == letter].sort_values("qualify_pct")
        colors = [
            "#1a9641" if p >= 66 else "#fdae61" if p >= 33 else "#d7191c"
            for p in group_df["qualify_pct"]
        ]
        bars = ax.barh(group_df["team"], group_df["qualify_pct"], color=colors, height=0.6)
        ax.set_xlim(0, 105)
        ax.set_title(f"Group {letter}", fontweight="bold", fontsize=11)
        ax.set_xlabel("Qualify %", fontsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.axvline(x=50, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)

        for bar, val in zip(bars, group_df["qualify_pct"]):
            ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                    f"{val:.0f}%", va="center", fontsize=8.5)

    plt.tight_layout()
    path = OUTPUT_DIR / "qualify_by_group.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chart 2 — Stacked finish-position bar for all 48 teams
# ---------------------------------------------------------------------------

def plot_finish_positions(df: pd.DataFrame) -> Path:
    sorted_df = df.sort_values(["group", "finish_1st_pct"], ascending=[True, False])

    fig, ax = plt.subplots(figsize=(22, 10))
    y = range(len(sorted_df))
    bottoms = [0.0] * len(sorted_df)

    for col, label, color in [
        ("finish_1st_pct", "1st place", POSITION_COLORS["1st"]),
        ("finish_2nd_pct", "2nd place", POSITION_COLORS["2nd"]),
        ("finish_3rd_pct", "3rd place", POSITION_COLORS["3rd"]),
        ("finish_4th_pct", "4th place", POSITION_COLORS["4th"]),
    ]:
        vals = sorted_df[col].tolist()
        ax.barh(list(y), vals, left=bottoms, color=color, label=label, height=0.7)
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    # Group dividers
    group_sizes = sorted_df.groupby("group").size()
    cumulative = 0
    for g in GROUP_LETTERS[:-1]:
        cumulative += group_sizes.get(g, 0)
        ax.axhline(y=cumulative - 0.5, color="white", linewidth=1.5)

    # Group labels on the right
    cumulative = 0
    for g in GROUP_LETTERS:
        size = group_sizes.get(g, 0)
        mid = cumulative + size / 2 - 0.5
        ax.text(102, mid, f"G{g}", va="center", fontsize=8, color="gray")
        cumulative += size

    ax.set_yticks(list(y))
    ax.set_yticklabels(sorted_df["team"].tolist(), fontsize=8)
    ax.set_xlim(0, 105)
    ax.set_xlabel("Finish probability (%)", fontsize=10)
    ax.set_title("2026 World Cup — Finish Position Distribution (10,000 simulations)",
                 fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=9)
    ax.axvline(x=100, color="lightgray", linewidth=0.8)

    plt.tight_layout()
    path = OUTPUT_DIR / "finish_positions.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chart 3 — Heatmap: qualify % across groups
# ---------------------------------------------------------------------------

def plot_qualification_heatmap(df: pd.DataFrame) -> Path:
    pivot = (
        df.set_index(["group", "team"])["qualify_pct"]
        .unstack("group")
        .reindex(columns=GROUP_LETTERS)
    )

    # For each group keep teams in finish order (highest qualify % first)
    ordered_rows: list[str] = []
    for g in GROUP_LETTERS:
        col_teams = df[df["group"] == g].sort_values("qualify_pct", ascending=False)["team"].tolist()
        ordered_rows.extend(col_teams)

    pivot = pivot.loc[ordered_rows]

    fig, ax = plt.subplots(figsize=(14, 14))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".0f",
        cmap="RdYlGn",
        vmin=0,
        vmax=100,
        linewidths=0.4,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": "Qualify %", "shrink": 0.6},
    )
    ax.set_title("2026 World Cup — Qualification % Heatmap\n(rows: teams sorted by qualify %; columns: groups)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Group", fontsize=10)
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelsize=10)
    ax.tick_params(axis="y", labelsize=8)

    plt.tight_layout()
    path = OUTPUT_DIR / "qualification_heatmap.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def generate_all(df: pd.DataFrame) -> None:
    paths = [
        plot_qualify_by_group(df),
        plot_finish_positions(df),
        plot_qualification_heatmap(df),
    ]
    for p in paths:
        print(f"Saved: {p}")


if __name__ == "__main__":
    from src.monte_carlo import run
    print("Running simulations...")
    results = run(n=10_000, seed=42)
    print("Generating charts...")
    generate_all(results)
