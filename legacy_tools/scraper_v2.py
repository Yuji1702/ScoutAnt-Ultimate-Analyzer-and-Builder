import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import sys

# Configuration
DB_PATH = "scoutant_v2/match_meta_db.json"
LINKS_FILE = "player_match_links.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_text(text):
    if not text: return ""
    return text.strip().replace('\xa0', ' ').replace('\n', ' ').replace('\t', '').strip()

def load_db():
    if not os.path.exists(DB_PATH):
        return {"matches": {}}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"matches": {}}

def save_db(data):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_match_id(url):
    match = re.search(r'vlr\.gg/(\d+)', url)
    return match.group(1) if match else None

def scrape_match_internal(match_url, db):
    match_id = extract_match_id(match_url)
    if not match_id:
        print(f"❌ Invalid URL: {match_url}")
        return

    # Check validity (optimistic check against ANY map for this match)
    # If we have match_id_*, we skip?
    # Valid check: if any key starts with match_id
    for key in db["matches"]:
        if key.startswith(f"{match_id}_"):
            print(f"⏭️  Skipping Match {match_id} (Already in DB)")
            return

    print(f"🔍 Analyzing Match: {match_id}")

    try:
        r = requests.get(match_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"❌ Failed to load page: {e}")
        return

    # 1. Get List of Maps (Mapping ID -> Name)
    map_dict = {} 
    nav_items = soup.select('div.vm-stats-gamesnav > div')
    for item in nav_items:
        gid = item.get('data-game-id')
        if gid and gid != 'all' and 'mod-disabled' not in item.get('class', []):
            raw = clean_text(item.get_text())
            name = re.sub(r'^\d+\s*', '', raw)
            name = re.sub(r'\s*\d+[:\-]\d+.*$', '', name).strip()
            map_dict[gid] = name
            
    # If no maps found (e.g. error page), return
    if not map_dict:
        print(f"⚠️  No maps found for {match_id}")
        return

    # 2. Iterate Game Divs
    game_divs = soup.select('div.vm-stats-game')
    scraped_count = 0
    
    for div in game_divs:
        game_id = div.get('data-game-id')
        
        if not game_id or game_id == 'all' or game_id not in map_dict:
            continue
            
        map_name = map_dict[game_id]
        unique_id = f"{match_id}_{game_id}"

        # Get Teams & Winner
        teams = div.select('div.vm-stats-game-header > div.team')
        if len(teams) < 2: continue
        
        team_data = []
        for tm in teams:
            name_div = tm.find('div', class_='team-name')
            t_name = clean_text(name_div.text) if name_div else "Unknown"
            is_win = bool(tm.find('div', class_='mod-win'))
            team_data.append({"name": t_name, "winner": is_win, "agents": []})
            
        winner = "Draw"
        if team_data[0]["winner"]: winner = team_data[0]["name"]
        elif team_data[1]["winner"]: winner = team_data[1]["name"]
        
        # Get Agents
        table = div.select_one('table.wf-table-inset.mod-overview')
        if not table: continue
            
        rows = table.find('tbody').find_all('tr')
        all_agents = []
        for row in rows:
            agent_cell = row.find('td', class_='mod-agents')
            if agent_cell:
                img = agent_cell.find('img')
                if img:
                    aname = img.get('title') or img.get('alt')
                    if aname: all_agents.append(clean_text(aname))
                    
        if len(all_agents) >= 10:
            team_data[0]["agents"] = all_agents[:5]
            team_data[1]["agents"] = all_agents[5:10]
            
            db["matches"][unique_id] = {
                "map": map_name,
                "winner": winner,
                "team_a": team_data[0]["name"],
                "team_a_agents": team_data[0]["agents"],
                "team_b": team_data[1]["name"],
                "team_b_agents": team_data[1]["agents"]
            }
            scraped_count += 1
            
    if scraped_count > 0:
        print(f"✅ Saved {scraped_count} maps for Match {match_id}")
    else:
        print(f"⚠️  No valid map data extracted for {match_id}")

def scrape_from_file():
    if not os.path.exists(LINKS_FILE):
        print(f"❌ File {LINKS_FILE} not found!")
        return

    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect all unique links
    all_links = set()
    for player, pdata in data.items():
        if "links" in pdata:
            for link in pdata["links"]:
                all_links.add(link)
    
    print(f"🎯 Found {len(all_links)} unique matches to process.")
    
    db = load_db()
    count = 0
    
    try:
        for link in all_links:
            scrape_match_internal(link, db)
            count += 1
            
            # Save every 10 matches to be safe
            if count % 10 == 0:
                save_db(db)
                print(f"💾 Checkpoint: Saved DB ({len(db['matches'])} matches total)")
                
            time.sleep(0.5) # Fast scraping since 1 request per match
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        save_db(db)
        print("💾 Final Save complete.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
         test_url = "https://www.vlr.gg/312779/gen-g-vs-sentinels-champions-tour-2024-masters-madrid-gf"
         scrape_match_internal(test_url, load_db())
    else:
        scrape_from_file()
