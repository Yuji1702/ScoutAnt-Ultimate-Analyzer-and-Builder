
import sys
import os
import json

# Add the project root to sys.path to allow imports
project_root = "C:/Users/dhruv/OneDrive/Desktop/ScoutAnt-Ultimate-Analyzer-and-Builder"
sys.path.append(project_root)

from analytics_system.analysis import process_match_query, process_player_query

def test_match():
    print("\n--- Testing Match Query (Prescriptive Analytics) ---")

    # Use a real map from the DB
    map_name = "Pearl"

    # Team A: Using real players from the DB
    team_a = [
        {"name": "murizzz", "agent": "Astra"},
        {"name": "kon4n", "agent": "Fade"},
        {"name": "snw", "agent": "Yoru"},
        {"name": "maestr0", "agent": "Neon"},
        {"name": "Zap", "agent": "Killjoy"},
    ]

    # Team B: Using real players from the DB
    # Based on the DB sample, Brinks was also playing Killjoy for the opponent
    team_b = [
        {"name": "Brinks", "agent": "Killjoy"},
        {"name": "Opponent2", "agent": "Jett"},
        {"name": "Opponent3", "agent": "Sova"},
        {"name": "Opponent4", "agent": "Omen"},
        {"name": "Opponent5", "agent": "Sage"},
    ]

    try:
        result = process_match_query(team_a, team_b, map_name)
        print(f"Map: {result['map']}")
        print(f"Meta Context: {result['prescriptive_analytics']['meta_context']}")
        print(f"Opponent Weaknesses: {result['prescriptive_analytics']['opponent_weaknesses']}")
        print("\nCounter Analysis:")
        for counter in result['prescriptive_analytics']['counter_analysis']:
            print(f" - {counter}")

        print(f"\nRecommended Composition for Team A: {result['prescriptive_analytics']['recommended_composition']}")
    except Exception as e:
        print(f"Match query failed: {e}")

def test_player():
    print("\n--- Testing Player Query (Recommendations) ---")

    # Use a real player name from the DB
    player_name = "murizzz"

    try:
        result = process_player_query(player_name)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            rec = result['recommendations']
            print(f"Player: {player_name}")
            print(f"Most Played Map: {rec['most_played_map']}")
            print(f"Recommended Agent: {rec['recommended_agent_on_most_played_map']}")
    except Exception as e:
        print(f"Player query failed: {e}")

if __name__ == "__main__":
    test_match()
    test_player()
