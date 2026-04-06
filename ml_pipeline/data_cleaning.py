"""
data_cleaning.py — Step 1: Load raw JSON and produce cleaned player-level data.

Reads match_stats_db.json, parses the "total attack defense" stat strings
into numeric arrays, filters bad data, and outputs player_stats.parquet.

Each row = one player's stats for one map in one match.
"""

import json
import os
import re
import numpy as np
import pandas as pd

from ml_pipeline.config import (
    RAW_DB_PATH, DATA_DIR, PLAYER_STATS_PARQUET,
    STAT_FIELDS, PHASES, STAT_COLUMN_MAP,
    AGENT_ROLE_MAP, BAD_AGENTS, BAD_MAPS,
)


def parse_stat_string(raw: str) -> list[float]:
    """
    Parse a stat string like "19 10 9" → [19.0, 10.0, 9.0].
    
    Handles edge cases:
      - "/ 17 9 8 /"  → strip slashes → [17.0, 9.0, 8.0]
      - "64% 79% 50%" → strip % → [64.0, 79.0, 50.0]
      - "+2 +1 +1"    → strip + → [2.0, 1.0, 1.0]
      - ""             → [0.0, 0.0, 0.0]
      - "5"            → [5.0, 0.0, 0.0]  (single value = total only)
    """
    if not raw or not isinstance(raw, str):
        return [0.0, 0.0, 0.0]

    # Remove /, %, + characters and extra whitespace
    cleaned = raw.replace("/", "").replace("%", "").replace("+", "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        return [0.0, 0.0, 0.0]

    parts = cleaned.split()

    try:
        values = [float(x) for x in parts]
    except ValueError:
        return [0.0, 0.0, 0.0]

    if len(values) == 3:
        return values
    elif len(values) == 1:
        return [values[0], 0.0, 0.0]
    elif len(values) == 2:
        return [values[0], values[1], 0.0]
    else:
        # More than 3 values — take first 3
        return values[:3]


def clean_match_data(db_path: str = RAW_DB_PATH) -> pd.DataFrame:
    """
    Load the raw JSON database and produce a cleaned player-level DataFrame.
    
    Returns:
        DataFrame with one row per player per map, all stats as numeric columns.
    """
    print("📂 Loading raw database...")
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    matches = data.get("matches", {})
    print(f"   Found {len(matches)} map entries")

    rows = []
    skipped_maps = 0
    skipped_agents = 0

    for key, match in matches.items():
        map_name = match.get("map", "")

        # Filter bad maps
        if map_name in BAD_MAPS or not map_name:
            skipped_maps += 1
            continue

        # Extract match_id and map_id from key (format: "matchId_mapId")
        parts = key.split("_", 1)
        match_id = parts[0]
        map_id = parts[1] if len(parts) > 1 else ""

        winner = match.get("winner", "")
        team_a = match.get("team_a", "")
        team_b = match.get("team_b", "")
        players = match.get("players", [])

        if len(players) < 10:
            skipped_maps += 1
            continue

        for player in players:
            agent = player.get("agent", "Unknown")

            # Filter bad agents
            if agent in BAD_AGENTS:
                skipped_agents += 1
                continue

            # Determine role
            role = AGENT_ROLE_MAP.get(agent, "Unknown")

            player_team = player.get("team", "")
            is_winner = 1 if player_team == winner else 0

            row = {
                "match_id":   match_id,
                "map_id":     map_id,
                "map":        map_name,
                "player_name": player.get("name", "Unknown"),
                "agent":      agent,
                "role":       role,
                "team":       player_team,
                "team_a":     team_a,
                "team_b":     team_b,
                "winner":     winner,
                "is_winner":  is_winner,
            }

            # Parse all stat fields into total/attack/defense columns
            for field in STAT_FIELDS:
                raw_val = player.get(field, "")
                parsed = parse_stat_string(raw_val)
                col_base = STAT_COLUMN_MAP.get(field, field)

                for i, phase in enumerate(PHASES):
                    row[f"{col_base}_{phase}"] = parsed[i]

            rows.append(row)

    print(f"   Skipped {skipped_maps} map entries (bad map or <10 players)")
    print(f"   Skipped {skipped_agents} player entries (bad agent)")

    df = pd.DataFrame(rows)

    # ─── Derived Features ────────────────────────────────────────────────
    # KD ratio (avoid division by zero)
    df["kd_ratio"] = df["kills_total"] / df["deaths_total"].replace(0, 1)
    df["kd_ratio_attack"] = df["kills_attack"] / df["deaths_attack"].replace(0, 1)
    df["kd_ratio_defense"] = df["kills_defense"] / df["deaths_defense"].replace(0, 1)

    # First kill / first death ratio
    df["fk_fd_ratio"] = df["first_kills_total"] / df["first_deaths_total"].replace(0, 1)

    print(f"✅ Cleaned DataFrame: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


def save_cleaned_data(df: pd.DataFrame, output_path: str = PLAYER_STATS_PARQUET):
    """Save cleaned DataFrame to Parquet."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_parquet(output_path, index=False)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"💾 Saved to {output_path} ({size_mb:.1f} MB)")


def run_cleaning(db_path: str = RAW_DB_PATH) -> pd.DataFrame:
    """Full cleaning pipeline: load → clean → save → return."""
    df = clean_match_data(db_path)
    save_cleaned_data(df)

    # Print summary stats
    print(f"\n📊 Data Summary:")
    print(f"   Unique players: {df['player_name'].nunique()}")
    print(f"   Unique maps:    {df['map'].nunique()}")
    print(f"   Unique agents:  {df['agent'].nunique()}")
    print(f"   Matches:        {df['match_id'].nunique()}")
    print(f"\n   Columns: {list(df.columns)}")
    print(f"\n   Sample row:\n{df.iloc[0].to_string()}")

    return df


if __name__ == "__main__":
    run_cleaning()
