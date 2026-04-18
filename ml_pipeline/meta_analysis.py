import pandas as pd
import os
from typing import List, Dict, Any
from ml_pipeline.config import PLAYER_STATS_PARQUET

# Persistent cache for the dataframe to avoid re-loading on every function call
_STATS_DF = None

def _get_df():
    global _STATS_DF
    if _STATS_DF is None:
        if os.path.exists(PLAYER_STATS_PARQUET):
            _STATS_DF = pd.read_parquet(PLAYER_STATS_PARQUET)
        else:
            # Fallback if file is missing (should not happen in this workspace)
            return pd.DataFrame()
    return _STATS_DF

def get_agent_win_rate(map_name: str, agent_name: str) -> float:
    """Calculates the win rate of a specific agent on a specific map."""
    df = _get_df()
    if df.empty: return 50.0
    
    mask = (df["map"] == map_name) & (df["agent"] == agent_name)
    relevant = df[mask]
    
    if relevant.empty: return 50.0
    return float(relevant["is_winner"].mean() * 100)

def get_top_agents_for_map(map_name: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """Returns the most successful agents on a given map."""
    df = _get_df()
    if df.empty: return []
    
    # Filter by map
    map_df = df[df["map"] == map_name]
    if map_df.empty: return []
    
    # Calculate stats per agent
    stats = map_df.groupby("agent").agg({
        "is_winner": "mean",
        "match_id": "nunique"
    }).reset_index()
    
    stats.columns = ["agent", "win_rate", "matches"]
    stats["win_rate"] = (stats["win_rate"] * 100).round(2)
    
    # Filter for agents with minimum sample size if needed
    results = stats.sort_values("win_rate", ascending=False).head(top_n)
    return results.to_dict("records")

def get_agent_vs_agent_win_rate(agent_a: str, agent_b: str) -> float:
    """Calculates how often Agent A wins when Agent B is on the opposing team."""
    df = _get_df()
    if df.empty: return 50.0
    
    # This is more complex: we need to find matches where both exist on DIFFERENT teams
    # 1. Matches where Agent A played
    matches_a = df[df["agent"] == agent_a][["match_id", "team", "is_winner"]]
    # 2. Matches where Agent B played
    matches_b = df[df["agent"] == agent_b][["match_id", "team"]]
    
    # Merge on match_id
    merged = pd.merge(matches_a, matches_b, on="match_id", suffixes=("_a", "_b"))
    
    # Filter for opposite teams
    opposing = merged[merged["team_a"] != merged["team_b"]]
    
    if opposing.empty: return 50.0
    
    return float(opposing["is_winner"].mean() * 100)

