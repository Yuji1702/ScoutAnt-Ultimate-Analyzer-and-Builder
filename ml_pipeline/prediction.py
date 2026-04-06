"""
prediction.py — Step 4: Prediction, simulation, and recommendation engine.

Provides:
  1. predict_player()      — Predicted rating/ACS for a player on a map with an agent
  2. predict_match()       — Win probability for team A vs team B
  3. simulate_team()       — Predicted team performance + win prob
  4. suggest_best_agent()  — Rank agents by predicted rating for a player on a map
  5. suggest_best_comp()   — Optimal agent assignment for 5 players on a map
"""

import os
import itertools
import numpy as np
import pandas as pd
import joblib

from ml_pipeline.config import (
    PLAYER_MODEL_PATH, MATCH_MODEL_PATH,
    PLAYER_FEATURES_PARQUET, PLAYER_STATS_PARQUET,
    MATCH_FEATURES_PARQUET,
    AGENT_ROLE_MAP, ROLES,
)


def _load_model(path):
    """Load a saved sklearn pipeline from disk."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}. Run model_training first.")
    return joblib.load(path)


def _load_player_features():
    """Load the player feature DataFrame."""
    return pd.read_parquet(PLAYER_FEATURES_PARQUET)


def _load_player_stats():
    """Load the raw player stats DataFrame."""
    return pd.read_parquet(PLAYER_STATS_PARQUET)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PLAYER PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

def predict_player(player_name: str, map_name: str, agent: str) -> dict:
    """
    Predict a player's performance (rating, ACS) on a given map with a given agent.
    
    Returns dict with predicted rating, ACS, attack/defense breakdown,
    and historical context.
    """
    model = _load_model(PLAYER_MODEL_PATH)
    player_feats = _load_player_features()

    role = AGENT_ROLE_MAP.get(agent, "Unknown")

    # Find historical data for this player+map+agent
    mask = (
        (player_feats["player_name"].str.lower() == player_name.lower()) &
        (player_feats["map"] == map_name) &
        (player_feats["agent"] == agent)
    )
    hist = player_feats[mask]

    # If no exact match, try player+map (any agent)
    if hist.empty:
        mask_any = (
            (player_feats["player_name"].str.lower() == player_name.lower()) &
            (player_feats["map"] == map_name)
        )
        hist = player_feats[mask_any]

    # If still nothing, try player (any map/agent) — use averages
    if hist.empty:
        mask_all = player_feats["player_name"].str.lower() == player_name.lower()
        hist = player_feats[mask_all]

    if hist.empty:
        return {"error": f"No historical data found for player '{player_name}'"}

    # Use the first/best match row to build input features
    ref = hist.iloc[0].copy()

    # Build input DataFrame matching model's expected columns
    input_row = {
        "map": map_name,
        "agent": agent,
        "role": role,
    }

    # Add numeric features from historical data
    numeric_cols = [c for c in hist.columns if c not in 
                    ["player_name", "map", "agent", "role", "rating_total", "acs_total"]]
    for col in numeric_cols:
        input_row[col] = ref[col] if col in ref.index else 0

    input_df = pd.DataFrame([input_row])

    # Predict
    prediction = model.predict(input_df)
    pred_rating = float(prediction[0][0])
    pred_acs = float(prediction[0][1])

    # Get attack/defense breakdown from historical data
    result = {
        "player":          player_name,
        "map":             map_name,
        "agent":           agent,
        "role":            role,
        "predicted_rating": round(pred_rating, 2),
        "predicted_acs":    round(pred_acs, 1),
        "historical": {
            "matches_played":   int(ref.get("match_count", 0)),
            "avg_rating":       round(float(ref.get("rating_total", 0)), 2),
            "avg_acs":          round(float(ref.get("acs_total", 0)), 1),
            "win_rate":         round(float(ref.get("win_rate", 0)) * 100, 1),
            "avg_kd_ratio":     round(float(ref.get("kd_ratio", 0)), 2),
            "rating_attack":    round(float(ref.get("rating_attack", 0)), 2),
            "rating_defense":   round(float(ref.get("rating_defense", 0)), 2),
            "acs_attack":       round(float(ref.get("acs_attack", 0)), 1),
            "acs_defense":      round(float(ref.get("acs_defense", 0)), 1),
        },
        "attack_vs_defense": {
            "stronger_side": "attack" if ref.get("rating_attack", 0) > ref.get("rating_defense", 0) else "defense",
            "rating_differential": round(
                float(ref.get("rating_attack", 0)) - float(ref.get("rating_defense", 0)), 2
            ),
        },
    }

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MATCH WIN PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

def _build_team_feature_vector(players: list[dict], prefix: str, player_feats: pd.DataFrame) -> dict:
    """
    Build team-level features from a list of player dicts.
    
    Each player dict: {"name": str, "agent": str}
    Looks up historical stats from player_features.parquet.
    """
    stats = []

    for p in players:
        name = p["name"]
        agent = p["agent"]
        role = AGENT_ROLE_MAP.get(agent, "Unknown")

        mask = (
            (player_feats["player_name"].str.lower() == name.lower()) &
            (player_feats["agent"] == agent)
        )
        hist = player_feats[mask]

        if hist.empty:
            mask_any = player_feats["player_name"].str.lower() == name.lower()
            hist = player_feats[mask_any]

        if not hist.empty:
            row = hist.iloc[0]
            stats.append({
                "rating_total": row.get("rating_total", 1.0),
                "acs_total":    row.get("acs_total", 200),
                "adr_total":    row.get("adr_total", 130),
                "kast_total":   row.get("kast_total", 65),
                "kd_ratio":     row.get("kd_ratio", 1.0),
                "fk_fd_ratio":  row.get("fk_fd_ratio", 1.0),
                "hs_pct_total": row.get("hs_pct_total", 20),
                "kills_total":  row.get("kills_total", 15),
                "deaths_total": row.get("deaths_total", 15),
                "first_kills_total": row.get("first_kills_total", 2),
                "first_deaths_total": row.get("first_deaths_total", 2),
                "role":         role,
                "rating_attack": row.get("rating_attack", 1.0),
                "rating_defense": row.get("rating_defense", 1.0),
            })
        else:
            # Default stats for unknown player
            stats.append({
                "rating_total": 1.0, "acs_total": 200, "adr_total": 130,
                "kast_total": 65, "kd_ratio": 1.0, "fk_fd_ratio": 1.0,
                "hs_pct_total": 20, "kills_total": 15, "deaths_total": 15,
                "first_kills_total": 2, "first_deaths_total": 2,
                "role": role,
                "rating_attack": 1.0, "rating_defense": 1.0,
            })

    stats_df = pd.DataFrame(stats)

    features = {}
    for col in ["rating_total", "acs_total", "adr_total", "kast_total",
                 "kd_ratio", "fk_fd_ratio", "hs_pct_total"]:
        features[f"{prefix}_{col}_avg"] = stats_df[col].mean()

    features[f"{prefix}_kills_sum"] = stats_df["kills_total"].sum()
    features[f"{prefix}_deaths_sum"] = stats_df["deaths_total"].sum()
    features[f"{prefix}_fk_sum"] = stats_df["first_kills_total"].sum()
    features[f"{prefix}_fd_sum"] = stats_df["first_deaths_total"].sum()

    role_counts = stats_df["role"].value_counts()
    for role in ROLES:
        features[f"{prefix}_num_{role.lower()}s"] = role_counts.get(role, 0)

    features[f"{prefix}_rating_attack_avg"] = stats_df["rating_attack"].mean()
    features[f"{prefix}_rating_defense_avg"] = stats_df["rating_defense"].mean()

    return features


def predict_match(
    team_a: list[dict], team_b: list[dict], map_name: str
) -> dict:
    """
    Predict win probability for team A vs team B.
    
    Args:
        team_a: List of 5 dicts with "name" and "agent" keys
        team_b: List of 5 dicts with "name" and "agent" keys  
        map_name: Map name (e.g. "Bind")
    
    Returns:
        Dict with win probabilities, strengths, weaknesses.
    """
    model = _load_model(MATCH_MODEL_PATH)
    player_feats = _load_player_features()

    ta_feats = _build_team_feature_vector(team_a, "ta", player_feats)
    tb_feats = _build_team_feature_vector(team_b, "tb", player_feats)

    row = {"map": map_name}
    row.update(ta_feats)
    row.update(tb_feats)

    # Delta features
    delta_cols = [
        ("rating_total_avg", "rating_total_avg"),
        ("acs_total_avg",    "acs_total_avg"),
        ("adr_total_avg",    "adr_total_avg"),
        ("kd_ratio_avg",     "kd_ratio_avg"),
        ("kills_sum",        "kills_sum"),
        ("fk_sum",           "fk_sum"),
    ]
    for ta_suffix, tb_suffix in delta_cols:
        row[f"delta_{ta_suffix}"] = ta_feats.get(f"ta_{ta_suffix}", 0) - tb_feats.get(f"tb_{tb_suffix}", 0)

    input_df = pd.DataFrame([row])

    # Ensure columns match what the model was trained on
    match_df = pd.read_parquet(MATCH_FEATURES_PARQUET)
    model_cols = [c for c in match_df.columns if c.startswith(("ta_", "tb_", "delta_")) or c == "map"]

    # Add missing columns with 0
    for col in model_cols:
        if col not in input_df.columns:
            input_df[col] = 0

    # Reorder to match training
    input_df = input_df[model_cols]

    proba = model.predict_proba(input_df)[0]
    team_a_win_prob = float(proba[1])
    team_b_win_prob = float(proba[0])

    # Analyze strengths
    strengths_a = []
    strengths_b = []
    if ta_feats.get("ta_rating_total_avg", 0) > tb_feats.get("tb_rating_total_avg", 0):
        strengths_a.append("Higher average rating")
    else:
        strengths_b.append("Higher average rating")

    if ta_feats.get("ta_fk_sum", 0) > tb_feats.get("tb_fk_sum", 0):
        strengths_a.append("More first kills")
    else:
        strengths_b.append("More first kills")

    if ta_feats.get("ta_kd_ratio_avg", 0) > tb_feats.get("tb_kd_ratio_avg", 0):
        strengths_a.append("Better K/D ratio")
    else:
        strengths_b.append("Better K/D ratio")

    if ta_feats.get("ta_rating_attack_avg", 0) > tb_feats.get("tb_rating_attack_avg", 0):
        strengths_a.append("Stronger attack side")
    else:
        strengths_b.append("Stronger attack side")

    if ta_feats.get("ta_rating_defense_avg", 0) > tb_feats.get("tb_rating_defense_avg", 0):
        strengths_a.append("Stronger defense side")
    else:
        strengths_b.append("Stronger defense side")

    return {
        "map": map_name,
        "team_a": {
            "players": team_a,
            "win_probability": round(team_a_win_prob * 100, 1),
            "avg_rating":      round(ta_feats.get("ta_rating_total_avg", 0), 2),
            "strengths":       strengths_a,
        },
        "team_b": {
            "players": team_b,
            "win_probability": round(team_b_win_prob * 100, 1),
            "avg_rating":      round(tb_feats.get("tb_rating_total_avg", 0), 2),
            "strengths":       strengths_b,
        },
        "prediction": "Team A" if team_a_win_prob > 0.5 else "Team B",
        "confidence":  round(max(team_a_win_prob, team_b_win_prob) * 100, 1),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_team(
    players: list[dict], opponent: list[dict], map_name: str
) -> dict:
    """
    Simulate a team's expected performance and win probability vs an opponent.
    
    Each dict: {"name": str, "agent": str}
    """
    # Individual predictions
    player_predictions = []
    for p in players:
        pred = predict_player(p["name"], map_name, p["agent"])
        player_predictions.append(pred)

    # Team match prediction
    match_pred = predict_match(players, opponent, map_name)

    return {
        "map":                map_name,
        "player_predictions": player_predictions,
        "match_prediction":   match_pred,
        "team_summary": {
            "avg_predicted_rating": round(
                np.mean([p.get("predicted_rating", 1.0) for p in player_predictions if "predicted_rating" in p]), 2
            ),
            "avg_predicted_acs": round(
                np.mean([p.get("predicted_acs", 200) for p in player_predictions if "predicted_acs" in p]), 1
            ),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. AGENT SUGGESTION
# ═══════════════════════════════════════════════════════════════════════════════

def suggest_best_agent(player_name: str, map_name: str, top_n: int = 5) -> dict:
    """
    Suggest the best agent for a player on a given map.
    
    Ranks all agents the player has history with by predicted rating.
    """
    player_feats = _load_player_features()

    # Find all agents this player has used
    mask = player_feats["player_name"].str.lower() == player_name.lower()
    player_data = player_feats[mask]

    if player_data.empty:
        return {"error": f"No data found for player '{player_name}'"}

    # Get agents played on this map, or all maps
    map_mask = player_data["map"] == map_name
    if map_mask.any():
        agents = player_data[map_mask]["agent"].unique()
    else:
        agents = player_data["agent"].unique()

    suggestions = []
    for agent in agents:
        try:
            pred = predict_player(player_name, map_name, agent)
            if "error" not in pred:
                suggestions.append({
                    "agent":            agent,
                    "role":             AGENT_ROLE_MAP.get(agent, "Unknown"),
                    "predicted_rating": pred["predicted_rating"],
                    "predicted_acs":    pred["predicted_acs"],
                    "matches_played":   pred["historical"]["matches_played"],
                    "historical_rating": pred["historical"]["avg_rating"],
                })
        except Exception:
            continue

    # Sort by predicted rating
    suggestions.sort(key=lambda x: x["predicted_rating"], reverse=True)

    return {
        "player":      player_name,
        "map":         map_name,
        "suggestions": suggestions[:top_n],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. COMPOSITION SUGGESTION
# ═══════════════════════════════════════════════════════════════════════════════

def suggest_best_composition(
    player_names: list[str], map_name: str, top_n: int = 5
) -> dict:
    """
    Suggest optimal agent assignments for a team of 5 players on a map.
    
    Tries combinations of each player's top agents and ranks by
    total predicted team rating.
    """
    player_feats = _load_player_features()

    # For each player, get their top agents on this map
    player_agent_options = []
    for name in player_names:
        mask = (
            (player_feats["player_name"].str.lower() == name.lower()) &
            (player_feats["map"] == map_name)
        )
        options = player_feats[mask].nlargest(5, "rating_total")[["agent", "rating_total"]].to_dict("records")

        if not options:
            # Fall back to any map
            mask_any = player_feats["player_name"].str.lower() == name.lower()
            options = player_feats[mask_any].nlargest(5, "rating_total")[["agent", "rating_total"]].to_dict("records")

        if not options:
            options = [{"agent": "Jett", "rating_total": 1.0}]

        player_agent_options.append(options)

    # Generate combinations (limit to avoid explosion)
    compositions = []
    for combo in itertools.product(*player_agent_options):
        agents = [c["agent"] for c in combo]

        # Check we don't have duplicate agents (each agent can only be picked once)
        if len(set(agents)) < len(agents):
            continue

        # Role distribution
        roles = [AGENT_ROLE_MAP.get(a, "Unknown") for a in agents]
        role_dist = {r: roles.count(r) for r in ROLES}

        # Total predicted rating
        total_rating = sum(c["rating_total"] for c in combo)

        # Bonus for balanced composition (at least 1 of each role)
        balance_bonus = sum(1 for v in role_dist.values() if v >= 1) * 0.1

        compositions.append({
            "players":    list(zip(player_names, agents)),
            "roles":      roles,
            "role_dist":  role_dist,
            "total_rating": round(total_rating, 2),
            "score":       round(total_rating + balance_bonus, 2),
        })

    compositions.sort(key=lambda x: x["score"], reverse=True)

    return {
        "map":            map_name,
        "player_names":   player_names,
        "compositions":   compositions[:top_n],
    }
