"""
feature_engineering.py — Step 2: Build player-level and match-level features.

Reads the cleaned player_stats.parquet and produces:
  1. player_features.parquet — aggregated historical stats per (player, map, agent)
  2. match_features.parquet — team-level features + label for win prediction
"""

import os
import numpy as np
import pandas as pd

from ml_pipeline.config import (
    DATA_DIR, PLAYER_STATS_PARQUET,
    PLAYER_FEATURES_PARQUET, MATCH_FEATURES_PARQUET,
    STAT_COLUMN_MAP, PHASES, ROLES,
)


# ─── Numeric stat columns we aggregate ───────────────────────────────────────

def _stat_columns() -> list[str]:
    """Return all numeric stat column names (base_phase combos)."""
    cols = []
    for field, col_base in STAT_COLUMN_MAP.items():
        for phase in PHASES:
            cols.append(f"{col_base}_{phase}")
    return cols


NUMERIC_STAT_COLS = _stat_columns() + [
    "kd_ratio", "kd_ratio_attack", "kd_ratio_defense", "fk_fd_ratio"
]


# ═══════════════════════════════════════════════════════════════════════════════
# PLAYER FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

def build_player_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate player stats across matches, grouped by (player_name, map, agent, role).
    
    For each group, compute:
      - mean of every numeric stat column
      - match count (sample size)
      - win rate
      - attack-defense differential for rating
    """
    print("🔧 Building player-level features...")

    group_cols = ["player_name", "map", "agent", "role"]

    # Aggregation: mean of stats + count + win rate
    agg_dict = {col: "mean" for col in NUMERIC_STAT_COLS if col in df.columns}
    agg_dict["is_winner"] = ["mean", "count"]

    grouped = df.groupby(group_cols, as_index=False).agg(agg_dict)

    # Flatten multi-level columns
    grouped.columns = [
        f"{a}_{b}" if b and b != "mean" else a
        for a, b in grouped.columns
    ]

    # Rename the aggregated columns
    grouped = grouped.rename(columns={
        "is_winner":       "win_rate",
        "is_winner_count": "match_count",
    })

    # Derived: attack-defense differential
    if "rating_attack" in grouped.columns and "rating_defense" in grouped.columns:
        grouped["rating_atk_def_diff"] = grouped["rating_attack"] - grouped["rating_defense"]

    if "acs_attack" in grouped.columns and "acs_defense" in grouped.columns:
        grouped["acs_atk_def_diff"] = grouped["acs_attack"] - grouped["acs_defense"]

    print(f"   ✅ Player features: {grouped.shape[0]} rows × {grouped.shape[1]} columns")
    return grouped


# ═══════════════════════════════════════════════════════════════════════════════
# TEAM & MATCH FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

def _team_features(team_df: pd.DataFrame, prefix: str) -> dict:
    """
    Compute aggregate features for one team in one match.
    
    Returns a flat dict with prefixed keys.
    """
    features = {}

    # Average stats
    for col in ["rating_total", "acs_total", "adr_total", "kast_total",
                 "kd_ratio", "fk_fd_ratio", "hs_pct_total"]:
        if col in team_df.columns:
            features[f"{prefix}_{col}_avg"] = team_df[col].mean()

    # Total kills / deaths
    if "kills_total" in team_df.columns:
        features[f"{prefix}_kills_sum"] = team_df["kills_total"].sum()
    if "deaths_total" in team_df.columns:
        features[f"{prefix}_deaths_sum"] = team_df["deaths_total"].sum()
    if "first_kills_total" in team_df.columns:
        features[f"{prefix}_fk_sum"] = team_df["first_kills_total"].sum()
    if "first_deaths_total" in team_df.columns:
        features[f"{prefix}_fd_sum"] = team_df["first_deaths_total"].sum()

    # Role distribution
    role_counts = team_df["role"].value_counts()
    for role in ROLES:
        features[f"{prefix}_num_{role.lower()}s"] = role_counts.get(role, 0)

    # Attack vs defense strength
    if "rating_attack" in team_df.columns:
        features[f"{prefix}_rating_attack_avg"] = team_df["rating_attack"].mean()
        features[f"{prefix}_rating_defense_avg"] = team_df["rating_defense"].mean()

    return features


def build_match_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build match-level feature vectors for win prediction.
    
    Each row = one match with team_a features, team_b features, deltas, and label.
    """
    print("🔧 Building match-level features...")

    # Group by (match_id, map_id) — each group has ~10 players
    match_groups = df.groupby(["match_id", "map_id"])

    match_rows = []

    for (match_id, map_id), group in match_groups:
        team_a_name = group["team_a"].iloc[0]
        team_b_name = group["team_b"].iloc[0]
        winner = group["winner"].iloc[0]
        map_name = group["map"].iloc[0]

        team_a_df = group[group["team"] == team_a_name]
        team_b_df = group[group["team"] == team_b_name]

        # Need exactly 5 players per team
        if len(team_a_df) < 5 or len(team_b_df) < 5:
            continue

        # Build feature dicts
        ta_feats = _team_features(team_a_df, "ta")
        tb_feats = _team_features(team_b_df, "tb")

        row = {
            "match_id": match_id,
            "map_id":   map_id,
            "map":      map_name,
            "team_a":   team_a_name,
            "team_b":   team_b_name,
        }
        row.update(ta_feats)
        row.update(tb_feats)

        # Delta features (team_a - team_b)
        delta_cols = [
            ("rating_total_avg", "rating_total_avg"),
            ("acs_total_avg",    "acs_total_avg"),
            ("adr_total_avg",    "adr_total_avg"),
            ("kd_ratio_avg",     "kd_ratio_avg"),
            ("kills_sum",        "kills_sum"),
            ("fk_sum",           "fk_sum"),
        ]
        for ta_suffix, tb_suffix in delta_cols:
            ta_val = ta_feats.get(f"ta_{ta_suffix}", 0)
            tb_val = tb_feats.get(f"tb_{tb_suffix}", 0)
            row[f"delta_{ta_suffix}"] = ta_val - tb_val

        # Label: team_a wins
        row["team_a_wins"] = 1 if winner == team_a_name else 0

        match_rows.append(row)

    match_df = pd.DataFrame(match_rows)
    print(f"   ✅ Match features: {match_df.shape[0]} rows × {match_df.shape[1]} columns")
    return match_df


# ═══════════════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════════════

def run_feature_engineering(player_stats_path: str = PLAYER_STATS_PARQUET):
    """Full feature engineering pipeline: load cleaned data → build features → save."""
    print("📂 Loading cleaned player stats...")
    df = pd.read_parquet(player_stats_path)
    print(f"   Loaded {df.shape[0]} rows")

    # Player features
    player_feats = build_player_features(df)
    os.makedirs(DATA_DIR, exist_ok=True)
    player_feats.to_parquet(PLAYER_FEATURES_PARQUET, index=False)
    size_mb = os.path.getsize(PLAYER_FEATURES_PARQUET) / (1024 * 1024)
    print(f"💾 Saved player features to {PLAYER_FEATURES_PARQUET} ({size_mb:.1f} MB)")

    # Match features
    match_feats = build_match_features(df)
    match_feats.to_parquet(MATCH_FEATURES_PARQUET, index=False)
    size_mb = os.path.getsize(MATCH_FEATURES_PARQUET) / (1024 * 1024)
    print(f"💾 Saved match features to {MATCH_FEATURES_PARQUET} ({size_mb:.1f} MB)")

    # Summary
    print(f"\n📊 Feature Summary:")
    print(f"   Player combos (name×map×agent): {player_feats.shape[0]}")
    print(f"   Match entries:                  {match_feats.shape[0]}")
    print(f"   Win rate distribution:\n{match_feats['team_a_wins'].value_counts().to_string()}")

    return player_feats, match_feats


if __name__ == "__main__":
    run_feature_engineering()
