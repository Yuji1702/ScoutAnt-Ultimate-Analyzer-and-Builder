import json
import os
from typing import List, Dict, Any

# Use absolute path for DB to avoid issues with current working directory
DB_PATH = "C:/Users/dhruv/OneDrive/Desktop/ScoutAnt-Ultimate-Analyzer-and-Builder/match_stats_db.json"

def load_db():
    if not os.path.exists(DB_PATH):
        return {"matches": {}}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"matches": {}}

def get_agent_win_rate(map_name: str, agent_name: str) -> float:
    """
    Calculates the win rate of a specific agent on a specific map.
    """
    db = load_db()
    matches = db.get("matches", {})

    wins = 0
    total = 0

    for match_id, data in matches.items():
        if data.get("map") != map_name:
            continue

        winner = data.get("winner")
        players = data.get("players", [])

        # Check if the agent was played in this match
        agent_played = any(p.get("agent") == agent_name for p in players)
        if not agent_played:
            continue

        # Check if the team playing this agent won
        for p in players:
            if p.get("agent") == agent_name:
                if p.get("team") == winner:
                    wins += 1
                    total += 1
                    break # count once per match

    return (wins / total * 100) if total > 0 else 0.0

def get_top_agents_for_map(map_name: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Returns the most successful agents on a given map.
    """
    db = load_db()
    matches = db.get("matches", {})

    agent_stats = {} # agent -> {wins: 0, total: 0}

    for match_id, data in matches.items():
        if data.get("map") != map_name:
            continue

        winner = data.get("winner")
        players = data.get("players", [])

        for p in players:
            agent = p.get("agent", "Unknown")
            if agent == "Unknown": continue

            if agent not in agent_stats:
                agent_stats[agent] = {"wins": 0, "total": 0}

            agent_stats[agent]["total"] += 1
            if p.get("team") == winner:
                agent_stats[agent]["wins"] += 1

    results = []
    for agent, stats in agent_stats.items():
        win_rate = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
        results.append({
            "agent": agent,
            "win_rate": round(win_rate, 2),
            "matches": stats["total"]
        })

    results.sort(key=lambda x: x["win_rate"], reverse=True)
    return results[:top_n]

def get_agent_vs_agent_win_rate(agent_a: str, agent_b: str) -> float:
    """
    Calculates how often Agent A wins when Agent B is on the opposing team.
    """
    db = load_db()
    matches = db.get("matches", {})

    wins_a = 0
    total_matchups = 0

    for match_id, data in matches.items():
        players = data.get("players", [])
        agents_present = [p.get("agent") for p in players]

        if agent_a in agents_present and agent_b in agents_present:
            winner = data.get("winner")
            # Find team of agent_a
            team_a = next((p.get("team") for p in players if p.get("agent") == agent_a), None)

            if team_a == winner:
                wins_a += 1
            total_matchups += 1

    return (wins_a / total_matchups * 100) if total_matchups > 0 else 50.0 # 50% default if no data
