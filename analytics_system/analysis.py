import pandas as pd
from typing import Dict, Any, List

from .utils import (
    load_player_features,
    get_role_for_agent,
    ROLES
)
from .prediction import predict_player_performance, predict_match_outcome

def analyze_team(players: List[Dict[str, str]], map_name: str) -> Dict[str, Any]:
    """
    Build the team block for the final JSON.
    players format: [{"name": "Player1", "agent": "Jett"}, ...]
    """
    team_data = {
        "players": [],
        "summary": {
            "avg_rating": 0.0,
            "avg_acs": 0.0,
            "role_distribution": {role.lower(): 0 for role in ROLES}
        }
    }

    total_rating = 0.0
    total_acs = 0.0
    for p in players:
        name = p["name"]
        agent = p["agent"]
        role = get_role_for_agent(agent)

        # Increment role
        role_key = role.lower()
        if role_key in team_data["summary"]["role_distribution"]:
            team_data["summary"]["role_distribution"][role_key] += 1
        else:
            team_data["summary"]["role_distribution"][role_key] = 1

        # Profile basic metrics + prediction
        player_pred = predict_player_performance(name, map_name, agent)
        
        # Calculate Flexibility and Best/Worst role for the player using all history
        player_feats = load_player_features()
        mask = player_feats["player_name"].str.lower() == name.lower()
        hist = player_feats[mask]

        best_role = "Unknown"
        worst_role = "Unknown"
        flex_score = 1

        if not hist.empty:
            role_perf = hist.groupby("role")["rating_total"].mean()
            if not role_perf.empty:
                best_role = role_perf.idxmax()
                worst_role = role_perf.idxmin()
            
            # Flex score = number of distinct roles played where matches > 0 (or just unique agents/roles)
            flex_score = len(hist["role"].unique())

        player_block = {
            "name": name,
            "agent": agent,
            "predicted_rating": player_pred["predicted_rating"],
            "predicted_acs": player_pred["predicted_acs"],
            "best_role": best_role,
            "worst_role": worst_role,
            "flexibility_score": flex_score
        }
        team_data["players"].append(player_block)
        total_rating += player_pred["predicted_rating"]
        total_acs += player_pred["predicted_acs"]

    if len(players) > 0:
        team_data["summary"]["avg_rating"] = round(total_rating / len(players), 2)
        team_data["summary"]["avg_acs"] = round(total_acs / len(players), 2)

    return team_data

def generate_insights(team_a_data: Dict[str, Any], team_b_data: Dict[str, Any]) -> List[str]:
    """
    Generate strings describing insights.
    """
    insights = []

    # Team rating comparison
    ta_rating = team_a_data["summary"]["avg_rating"]
    tb_rating = team_b_data["summary"]["avg_rating"]
    if ta_rating > tb_rating:
        insights.append("Team A has a stronger overall average rating.")
    elif tb_rating > ta_rating:
        insights.append("Team B has a stronger overall average rating.")

    for team_name, team_info in [("Team A", team_a_data), ("Team B", team_b_data)]:
        roles = team_info["summary"]["role_distribution"]
        if roles.get("duelist", 0) == 0:
            insights.append(f"{team_name} lacks a duelist.")
        if roles.get("controller", 0) == 0:
            insights.append(f"{team_name} lacks a controller (smokes).")
        if roles.get("initiator", 0) == 0:
            insights.append(f"{team_name} lacks an initiator for intel/flashes.")
        if roles.get("sentinel", 0) == 0:
            insights.append(f"{team_name} lacks a sentinel for flank watch and site hold.")

        # Check players for out of role
        for p in team_info["players"]:
            current_role = get_role_for_agent(p["agent"])
            if current_role == p["worst_role"] and current_role != "Unknown":
                insights.append(f"{p['name']} is playing their worst role ({current_role}). Switch them to {p['best_role']} for better performance.")
            elif current_role == p["best_role"] and current_role != "Unknown":
                insights.append(f"{p['name']} is on their most comfortable role ({current_role}).")

    if team_a_data["summary"]["role_distribution"].get("duelist", 0) >= 3:
        insights.append("Team A has too many duelists. Suggested: adjust roles for better balance.")
    if team_b_data["summary"]["role_distribution"].get("duelist", 0) >= 3:
        insights.append("Team B has too many duelists. Suggested: adjust roles for better balance.")

    # Deduplicate and sort insights
    return list(dict.fromkeys(insights))

def generate_reasoning(team_a_data: Dict[str, Any], team_b_data: Dict[str, Any]) -> List[str]:
    """
    Generate human-readable reasoning explaining why the model predicts as it does.
    """
    reasoning = []
    
    # Rating comparison
    if team_a_data["summary"]["avg_rating"] > team_b_data["summary"]["avg_rating"]:
        reasoning.append("Team A has higher average rating based on historical performance.")
    elif team_b_data["summary"]["avg_rating"] > team_a_data["summary"]["avg_rating"]:
        reasoning.append("Team B has higher average rating based on historical performance.")

    # ACS comparison
    if team_a_data["summary"]["avg_acs"] > team_b_data["summary"]["avg_acs"]:
        reasoning.append("Team A shows stronger combat score (ACS).")
    elif team_b_data["summary"]["avg_acs"] > team_a_data["summary"]["avg_acs"]:
        reasoning.append("Team B shows stronger combat score (ACS).")

    # Missing Roles Comparison
    for team_name, team_info in [("Team A", team_a_data), ("Team B", team_b_data)]:
        roles = team_info["summary"]["role_distribution"]
        if roles.get("duelist", 0) == 0:
            reasoning.append(f"{team_name} lacks a duelist.")
        if roles.get("controller", 0) == 0:
            reasoning.append(f"{team_name} lacks a controller (smokes).")

    return reasoning

def process_match_query(team_a: List[Dict[str, str]], team_b: List[Dict[str, str]], map_name: str) -> Dict[str, Any]:
    """
    Produces final JSON matching output schema.
    """
    ta_data = analyze_team(team_a, map_name)
    tb_data = analyze_team(team_b, map_name)

    match_probs = predict_match_outcome(team_a, team_b, map_name)

    insights = generate_insights(ta_data, tb_data)
    reasoning = generate_reasoning(ta_data, tb_data)
    
    # Confidence tag
    max_prob = max(match_probs["team_a_win_probability"], match_probs["team_b_win_probability"])
    if max_prob >= 0.65:
        confidence = "High"
    elif 0.55 <= max_prob < 0.65:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "map": map_name,
        "team_a_win_probability": match_probs["team_a_win_probability"],
        "team_b_win_probability": match_probs["team_b_win_probability"],
        "confidence": confidence,
        "model_reasoning": reasoning,
        "team_a": ta_data,
        "team_b": tb_data,
        "insights": insights,
        "note": "Predictions are probabilistic and not guaranteed outcomes."
    }

def process_player_query(player_name: str) -> Dict[str, Any]:
    """
    Produces a full player profile module output.
    """
    player_feats = load_player_features()
    mask = player_feats["player_name"].str.lower() == player_name.lower()
    hist = player_feats[mask]

    if hist.empty:
        return {"error": f"No data found for {player_name}"}

    total_matches = int(hist["match_count"].sum() if "match_count" in hist.columns else len(hist))
    
    # Calculate averages
    avg_rating = round(hist["rating_total"].mean(), 2)
    avg_acs = round(hist["acs_total"].mean(), 2)
    avg_kd = round(hist["kd_ratio"].mean(), 2)
    avg_kast = round(hist["kast_total"].mean(), 2)
    avg_adr = round(hist["adr_total"].mean(), 2)

    # Role Performance
    role_perf = hist.groupby("role")["rating_total"].mean().round(2).to_dict()
    main_role = max(role_perf, key=role_perf.get) if role_perf else "Unknown"

    flex_score = len(role_perf)

    # Agent Performance
    if "match_count" in hist.columns:
        agent_perf = hist.groupby("agent").agg({"rating_total": "mean", "match_count": "sum"}).to_dict("index")
    else:
        agent_perf = hist.groupby("agent").agg({"rating_total": "mean"}).to_dict("index")
        for k in agent_perf:
            agent_perf[k]["match_count"] = len(hist[hist["agent"] == k])

    for k in agent_perf:
        agent_perf[k]["rating_total"] = round(agent_perf[k]["rating_total"], 2)

    strengths = []
    weaknesses = []

    if avg_rating > 1.10: strengths.append("High overall impact (Rating > 1.10).")
    if avg_rating < 0.90: weaknesses.append("Low overall impact (Rating < 0.90).")
    if avg_acs > 230: strengths.append("High combat score.")
    if avg_acs < 180: weaknesses.append("Low combat score, struggles in direct engagements.")
    if avg_kd > 1.1: strengths.append("Consistently positive kill/death ratio.")
    if avg_kd < 0.9: weaknesses.append("Tends to die more frequently than securing kills.")

    return {
        "player_name": player_name,
        "total_matches": total_matches,
        "main_role": main_role,
        "flexibility_score": flex_score,
        "average_stats": {
            "rating": avg_rating,
            "acs": avg_acs,
            "kd_ratio": avg_kd,
            "kast": avg_kast,
            "adr": avg_adr
        },
        "role_performance": role_perf,
        "agent_performance": agent_perf,
        "strengths": strengths,
        "weaknesses": weaknesses
    }
