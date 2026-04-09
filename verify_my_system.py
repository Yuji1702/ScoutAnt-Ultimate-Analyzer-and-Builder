import json
import os
import sys

# Add the project root to sys.path so we can import from analytics_system
project_root = "C:/Users/dhruv/OneDrive/Desktop/ScoutAnt-Ultimate-Analyzer-and-Builder"
sys.path.append(project_root)

from analytics_system.analysis import process_match_query, process_player_query

def main():
    # Using players actually found in the match_stats_db.json
    team_a = [
        {"name": "murizzz", "agent": "Astra"},
        {"name": "kon4n", "agent": "Fade"},
        {"name": "snw", "agent": "Yoru"},
        {"name": "maestr0", "agent": "Neon"},
        {"name": "Zap", "agent": "Killjoy"}
    ]

    team_b = [
        {"name": "Brinks", "agent": "Killjoy"},
        {"name": "PlayerX", "agent": "Jett"}, # Intentional unknown
        {"name": "PlayerY", "agent": "Sova"},
        {"name": "PlayerZ", "agent": "Omen"},
        {"name": "PlayerW", "agent": "Sova"}
    ]

    print("--- Verifying Match Query (Team Impact) ---")
    try:
        # Testing on 'Pearl' as it was seen in the DB
        result = process_match_query(team_a, team_b, "Pearl")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Match Query Failed: {e}")

    print("\n\n--- Verifying Player Query (Individual Profile) ---")
    try:
        # Testing with 'murizzz' who is definitely in the DB
        player_res = process_player_query("murizzz")
        print(f"Profile for murizzz:\n{json.dumps(player_res, indent=2)}")
    except Exception as e:
        print(f"❌ Player Query Failed: {e}")

if __name__ == "__main__":
    main()
