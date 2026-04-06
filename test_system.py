import json
from analytics_system.analysis import process_match_query, process_player_query

def main():
    # Setup some dummy or real players (Assuming Player1 won't be found but TenZ or similar might be in the db)
    # Using real players might be better to see data, but we don't know the exact names.
    # Player1 -> Fallbacks to 1.0 rating, 200 ACS
    team_a = [
        {"name": "TenZ", "agent": "Jett"},
        {"name": "Zellsis", "agent": "KAY/O"},
        {"name": "johnqt", "agent": "Cypher"},
        {"name": "Sacy", "agent": "Sova"},
        {"name": "Oxy", "agent": "Omen"}
    ]
    
    team_b = [
        {"name": "Demon1", "agent": "Jett"},
        {"name": "Ethan", "agent": "Skye"},
        {"name": "jawgemo", "agent": "Raze"}, # 2 duelists
        {"name": "Boostio", "agent": "Killjoy"},
        {"name": "C0M", "agent": "Sova"} # no controller
    ]

    print("--- Testing process_match_query ---")
    result = process_match_query(team_a, team_b, "Pearl")
    print(json.dumps(result, indent=2))

    print("\n\n--- Testing process_player_query ---")
    # Query for a non-existent player
    player_res_1 = process_player_query("PlayerXYZ")
    print("PlayerXYZ:", json.dumps(player_res_1, indent=2))

    # Query for a known player (hopefully)
    player_res_2 = process_player_query("TenZ")
    print("TenZ:", json.dumps(player_res_2, indent=2))

if __name__ == "__main__":
    main()
