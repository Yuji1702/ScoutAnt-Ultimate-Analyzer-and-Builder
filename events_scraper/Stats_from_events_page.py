import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import sys

# Configuration
DB_PATH = "match_stats_db.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_text(text):
    if not text: return ""
    return text.strip().replace('\xa0', ' ').replace('\n', ' ').replace('\t', '').strip()

def load_db():
    if not os.path.exists(DB_PATH):
        print("  creating new db matches dict")
        return {"matches": {}}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception:
        return {"matches": {}}

def save_db(data):
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Event Crawler ---

def get_completed_events_all_pages(start_page=1):
    events = []
    page = start_page
    
    while True:
        url = f"https://www.vlr.gg/events/?tier=all&region=all&status=completed&page={page}"
        print(f"🌍 Fetching Events Page {page}: {url}...")
        
        try:
            r = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            event_links = soup.select('a.event-item')
            
            if not event_links:
                print(f"📍 No events found on page {page}. Stopping.")
                break
                
            print(f"📍 Found {len(event_links)} events on page {page}.")
            
            for link in event_links:
                href = link.get('href')
                full_url = "https://www.vlr.gg" + href
                events.append(full_url)
            
            page += 1
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error fetching events page {page}: {e}")
            break
            
    return events

def get_matches_from_event(event_url):
    match_urls = []
    seen = set()
    
    try:
        r = requests.get(event_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if re.match(r'^/\d+/', href):
                if not href.startswith('/event') and not href.startswith('/team'):
                     full_url = "https://www.vlr.gg" + href
                     if full_url not in seen:
                         match_urls.append(full_url)
                         seen.add(full_url)
        
    except Exception as e:
        print(f"    ❌ Error crawling event: {e}")
        
    return match_urls

def parse_stats_row(row):
    cols = row.find_all('td')
    if not cols: return None
    
    def txt(i):
        if i < len(cols):
            return clean_text(cols[i].get_text())
        return "0"

    player_cell = row.find('td', class_='mod-player') 
    if not player_cell: return None
    
    name_div = player_cell.find('div', class_='text-of')
    name = clean_text(name_div.text) if name_div else "Unknown"
    
    agent_cell = row.find('td', class_='mod-agents')
    agent = "Unknown"
    if agent_cell:
        img = agent_cell.find('img')
        if img:
            agent = img.get('title') or img.get('alt')
            
    try:
        return {
            "name": name,
            "agent": agent,
            "rating": txt(2),
            "acs": txt(3),
            "k": txt(4),
            "d": txt(5),
            "a": txt(6),
            "kd_diff": txt(7),
            "kast": txt(8),
            "adr": txt(9),
            "hs_percent": txt(10),
            "fk": txt(11),
            "fd": txt(12)
        }
    except:
        return None

def scrape_match_detailed(match_url, db):
    match_id = re.search(r'vlr\.gg/(\d+)', match_url).group(1)
    
    for k in db["matches"]:
        if k.startswith(f"{match_id}_"):
             return

    print(f"  ⚔️ Scraping Match: {match_id}")
    
    try:
        r = requests.get(match_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
    except Exception as e:
        print(f"    ❌ Failed to load: {e}")
        return

    map_dict = {}
    nav = soup.select('div.vm-stats-gamesnav > div')
    for item in nav:
        gid = item.get('data-game-id')
        if gid and gid != 'all' and 'mod-disabled' not in item.get('class', []):
            raw = clean_text(item.get_text())
            name = re.sub(r'^\d+\s*', '', raw)
            name = re.sub(r'\s*\d+[:\-]\d+.*$', '', name).strip()
            map_dict[gid] = name
            
    game_divs = soup.select('div.vm-stats-game')
    maps_saved = 0
    
    for div in game_divs:
        game_id = div.get('data-game-id')
        if not game_id or game_id == 'all' or game_id not in map_dict:
            continue
            
        map_name = map_dict[game_id]
        unique_id = f"{match_id}_{game_id}"
        
        teams = div.select('div.vm-stats-game-header > div.team')
        if len(teams) < 2: continue
        
        t1_name = clean_text(teams[0].find('div', class_='team-name').text)
        t2_name = clean_text(teams[1].find('div', class_='team-name').text)
        
        winner = "Draw"
        if teams[0].find('div', class_='mod-win'): winner = t1_name
        elif teams[1].find('div', class_='mod-win'): winner = t2_name
        
        tables = div.select('table.wf-table-inset.mod-overview')
        
        if not tables: 
            continue
        
        players = []
        for table in tables:
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                if row.get('class') and 'mod-header' in row.get('class'): continue
                p = parse_stats_row(row)
                if p: players.append(p)
            
        if len(players) >= 10:
            mid = len(players) // 2
            for i, p in enumerate(players):
                p['team'] = t1_name if i < mid else t2_name
                
            db["matches"][unique_id] = {
                "map": map_name,
                "winner": winner,
                "team_a": t1_name,
                "team_b": t2_name,
                "players": players
            }
            maps_saved += 1
            
    if maps_saved > 0:
        print(f"    ✅ Saved {maps_saved} maps.")

def main():
    print("🚀 Starting ScoutAnt Event Crawler (Paged Mode)...")
    db = load_db()
    
    event_urls = get_completed_events_all_pages(start_page=1)
    
    print(f"🎯 Collected {len(event_urls)} events. Processing matches...")
    
    for i, event_url in enumerate(event_urls):
        match_urls = get_matches_from_event(event_url)
        
        for m_url in match_urls:
            scrape_match_detailed(m_url, db)
            time.sleep(0.5)
            
        if i % 2 == 0:
             save_db(db)
             print(f"💾 Checkpoint: {len(db['matches'])} total map stats stored.")

    save_db(db)
    print("\n🎉 Done!")

if __name__ == "__main__":
    main()
