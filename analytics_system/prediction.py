import pandas as pd
from typing import Dict, Any, List

from .utils import (
    load_player_model,
    load_match_model,
    load_player_features,
    load_match_features,
    get_role_for_agent,
    ROLES
)


def predict_player_performance(player_name: str, map_name: str, agent: str) -> Dict[str, Any]:
    """
    Predict a player's performance (rating, ACS) on a given map with a given agent.
    If exact historical data isn't found, falls back to map averages, then overall averages.
    """
    model = load_player_model()
    player_feats = load_player_features()

    role = get_role_for_agent(agent)

    # Filter rules as requested: player name -> map -> agent
    mask = (
        (player_feats["player_name"].str.lower() == player_name.lower()) &
        (player_feats["map"] == map_name) &
        (player_feats["agent"] == agent)
    )
    hist = player_feats[mask]

    # Fallback to map-only
    if hist.empty:
        mask_any = (
            (player_feats["player_name"].str.lower() == player_name.lower()) &
            (player_feats["map"] == map_name)
        )
        hist = player_feats[mask_any]

    # Fallback to player only
    if hist.empty:
        mask_all = player_feats["player_name"].str.lower() == player_name.lower()
        hist = player_feats[mask_all]

    # If completely empty, use global generic averages
    if hist.empty:
        ref = pd.Series({
            "rating_total": 1.0, "acs_total": 200, "kd_ratio": 1.0, 
            "kast_total": 70, "adr_total": 130
        })
    else:
        # Compute averages as requested
        ref = hist.mean(numeric_only=True)

    input_row = {
        "map": map_name,
        "agent": agent,
        "role": role,
    }

    # Populate numerical features
    # Get columns from the model's feature names (it's a pipeline, so we inspect preprocessor or just supply them)
    # The original ML pipeline expects the same columns as in the dataframe minus target columns.
    numeric_cols = [c for c in player_feats.columns if c not in 
                    ["player_name", "map", "agent", "role", "rating_total", "acs_total", "date", "match_id"]]
    
    for col in numeric_cols:
        input_row[col] = ref.get(col, 0)

    input_df = pd.DataFrame([input_row])

    # Ensure all required features are present
    try:
        prediction = model.predict(input_df)
        pred_rating = float(prediction[0][0])
        pred_acs = float(prediction[0][1])
    except Exception as e:
        # Fallback if prediction fails
        pred_rating = 1.0
        pred_acs = 200.0

    return {
        "predicted_rating": round(pred_rating, 2),
        "predicted_acs": round(pred_acs, 2),
        "historical_avg_rating": round(ref.get("rating_total", 0), 2),
        "historical_avg_acs": round(ref.get("acs_total", 0), 2),
        "kd_ratio": round(ref.get("kd_ratio", 1.0), 2),
        "kast": round(ref.get("kast_total", 70), 2),
        "adr": round(ref.get("adr_total", 130), 2)
    }


def build_team_feature_vector(players: List[Dict[str, str]], prefix: str, player_feats: pd.DataFrame) -> Dict[str, float]:
    """
    Build raw statistics dict for a team.
    players format: [{"name": "Player1", "agent": "Jett"}, ...]
    """
    stats = []

    for p in players:
        name = p["name"]
        agent = p["agent"]
        role = get_role_for_agent(agent)

        mask = (
            (player_feats["player_name"].str.lower() == name.lower()) &
            (player_feats["agent"] == agent)
        )
        hist = player_feats[mask]

        if hist.empty:
            mask_any = player_feats["player_name"].str.lower() == name.lower()
            hist = player_feats[mask_any]

        if not hist.empty:
            row = hist.mean(numeric_only=True)
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


def predict_match_outcome(team_a: List[Dict[str, str]], team_b: List[Dict[str, str]], map_name: str) -> Dict[str, float]:
    """
    Predict win probabilities for Team A vs Team B.
    """
    model = load_match_model()
    player_feats = load_player_features()

    ta_feats = build_team_feature_vector(team_a, "ta", player_feats)
    tb_feats = build_team_feature_vector(team_b, "tb", player_feats)

    row = {"map": map_name}
    row.update(ta_feats)
    row.update(tb_feats)

    # Delta features map
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

    # Make sure we have the right columns
    # Optimization: We know which columns the model expects based on the features we just built
    # Instead of loading a huge parquet file just for column names, we use the known schema
    model_cols = ["map"] + list(ta_feats.keys()) + list(tb_feats.keys())
    for ta_suffix, _ in delta_cols:
        model_cols.append(f"delta_{ta_suffix}")

    for col in model_cols:
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[model_cols]

    try:
        proba = model.predict_proba(input_df)[0]
        team_b_win_prob = float(proba[0])
        team_a_win_prob = float(proba[1])
    except Exception as e:
        team_a_win_prob = 0.5
        team_b_win_prob = 0.5

    return {
        "team_a_win_probability": round(team_a_win_prob, 2),
        "team_b_win_probability": round(team_b_win_prob, 2)
    }
