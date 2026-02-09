import json
import os
import statistics

DB_PATH = "match_stats_db.json"

def load_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ DB not found: {DB_PATH}")
        return {"matches": {}}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading DB: {e}")
        return {"matches": {}}

def get_meta_compositions(map_name, top_n=5):
    """
    Returns the most successful agent compositions for a given map.
    """
    db = load_db()
    matches = db.get("matches", {})
    
    compositions = {}
    
    for match_id, data in matches.items():
        if data.get("map") != map_name:
            continue
            
        winner = data.get("winner")
        team_a = data.get("team_a")
        team_b = data.get("team_b")
        
        winning_team_players = []
        if winner == team_a:
            winning_team_players = [p for p in data["players"] if p.get("team") == team_a]
        elif winner == team_b:
            winning_team_players = [p for p in data["players"] if p.get("team") == team_b]
            
        agents = sorted([p.get("agent", "Unknown") for p in winning_team_players])
        if len(agents) < 5: continue 
        
        comp_key = tuple(agents)
        if comp_key not in compositions:
            compositions[comp_key] = {"wins": 0, "total": 0}
            
        compositions[comp_key]["wins"] += 1
        compositions[comp_key]["total"] += 1
        
        losing_team_players = []
        if winner == team_a:
            losing_team_players = [p for p in data["players"] if p.get("team") == team_b]
        else:
            losing_team_players = [p for p in data["players"] if p.get("team") == team_a]
            
        l_agents = sorted([p.get("agent", "Unknown") for p in losing_team_players])
        if len(l_agents) < 5: continue
        
        l_key = tuple(l_agents)
        if l_key not in compositions:
            compositions[l_key] = {"wins": 0, "total": 0}
        compositions[l_key]["total"] += 1

    results = []
    for comp, stats in compositions.items():
        win_rate = (stats["wins"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        results.append({
            "agents": list(comp),
            "wins": stats["wins"],
            "matches": stats["total"],
            "win_rate": round(win_rate, 1)
        })
        
    results.sort(key=lambda x: x["win_rate"], reverse=True)
    return results[:top_n]

def predict_match(player_name, map_name, agent):
    """
    Predicts player performance based on historical data.
    """
    db = load_db()
    matches = db.get("matches", {})
    
    player_stats = []
    
    for match_id, data in matches.items():
        if data.get("map") != map_name: continue
        
        for p in data["players"]:
            if p.get("name").lower() == player_name.lower():
                if agent and p.get("agent").lower() == agent.lower():
                    try:
                        acs_val = p.get("acs") or "0"
                        if acs_val == "": acs_val = "0"
                        
                        k_val = p.get("k", "0")
                        d_val = p.get("d", "0")
                        
                        acs = float(acs_val)
                        k = int(k_val)
                        d = int(d_val)
                        player_stats.append({"acs": acs, "k": k, "d": d})
                    except:
                        pass
                    
    if not player_stats:
        return {"error": "No data found"}
        
    avg_acs = statistics.mean([s["acs"] for s in player_stats])
    avg_k = statistics.mean([s["k"] for s in player_stats])
    avg_d = statistics.mean([s["d"] for s in player_stats])
    
    return {
        "prediction": {
            "player": player_name,
            "map": map_name,
            "agent": agent,
            "avg_acs": round(avg_acs, 1),
            "avg_kills": round(avg_k, 1),
            "avg_deaths": round(avg_d, 1),
            "samples": len(player_stats)
        }
    }

if __name__ == "__main__":
    db = load_db()
    matches = db.get("matches", {})
    if not matches:
        print("❌ No matches loaded.")
    else:
        all_maps = set(m.get("map") for m in matches.values())
        print(f"🌍 Found Maps: {all_maps}")
        
        test_map = list(all_maps)[0] if all_maps else "Bind"
        print(f"\n🔎 Analyzing Meta for '{test_map}'...")
        meta = get_meta_compositions(test_map)
        for i, m in enumerate(meta):
            print(f"  #{i+1}: {m['agents']} | WR: {m['win_rate']}% ({m['wins']}/{m['matches']})")
            
        print("\n🔮 Testing Prediction...")
        first_match = next(iter(matches.values()))
        p_name = first_match["players"][0]["name"]
        p_map = first_match["map"]
        p_agent = first_match["players"][0]["agent"]
        
        print(f"Predicting for {p_name} on {p_map} ({p_agent})...")
        pred = predict_match(p_name, p_map, p_agent)
        print(pred)
