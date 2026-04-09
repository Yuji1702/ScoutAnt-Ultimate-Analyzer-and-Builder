from typing import List, Dict, Any
from .meta_analysis import get_agent_win_rate, get_top_agents_for_map, get_agent_vs_agent_win_rate

def find_best_counter(opponent_agent: str, map_name: str) -> Dict[str, Any]:
    """
    Finds the agent that historically performs best against the opponent's agent
    while remaining viable on the specific map.
    """
    # Get top viable agents for this map to ensure the counter is actually good on the map
    top_agents = get_top_agents_for_map(map_name, top_n=10)
    if not top_agents:
        return {"agent": "Unknown", "reason": "No map data available"}

    best_counter = None
    highest_win_rate = -1.0

    # We iterate through the top viable agents on the map and see who counters the opponent best
    for entry in top_agents:
        agent = entry["agent"]
        if agent == opponent_agent:
            continue

        # Win rate of this agent vs the opponent agent
        win_rate = get_agent_vs_agent_win_rate(agent, opponent_agent)

        # We prioritize agents that have a high win rate against the opponent
        # AND are historically strong on the map
        score = win_rate * (1 + (entry["win_rate"] / 100))

        if score > highest_win_rate:
            highest_win_rate = score
            best_counter = agent

    if best_counter:
        return {
            "agent": best_counter,
            "reason": f"Historically successful against {opponent_agent} and strong on {map_name}."
        }

    return {"agent": "Unknown", "reason": "No significant counter found."}

def analyze_composition_weakness(opponent_comp: List[str]) -> List[str]:
    """
    Identifies missing roles or specific vulnerabilities in the opponent's agent selection.
    Note: This requires mapping agents to roles.
    """
    from .config import ROLES, AGENT_ROLE_MAP

    opponent_roles = [AGENT_ROLE_MAP.get(agent, "Unknown") for agent in opponent_comp]
    weaknesses = []

    for role in ROLES:
        if role not in opponent_roles:
            weaknesses.append(f"Opponent lacks a {role}, creating a strategic opening for map control.")

    if len(opponent_comp) > 0:
        duelists = [a for a in opponent_comp if AGENT_ROLE_MAP.get(a, "Unknown") == "Duelist"]
        if len(duelists) == 0:
            weaknesses.append("Opponent has no primary entry/duelist, potentially struggling with site takes.")
        elif len(duelists) >= 3:
            weaknesses.append("Opponent is over-reliant on duelists, lacking utility depth.")

    return weaknesses
