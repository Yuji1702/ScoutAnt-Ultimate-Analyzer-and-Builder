import requests
from bs4 import BeautifulSoup
import json
import re
import time

def clean_name(name):
    return name.strip().lower().replace(" ", "")

def get_vlr_ids_for_players(player_names):
    base_url = "https://www.vlr.gg/search/?q="
    player_info_list = []

    for name in player_names:
        print(f"\n🔍 Searching for '{name}'...")
        url = base_url + name.replace(" ", "+")
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')

        # Try exact match first
        link = soup.find('a', href=re.compile(r'/player/\d+/'), string=re.compile(name, re.I))
        if not link:
            link = soup.find('a', href=re.compile(r'/player/\d+/'))

        if not link:
            print(f"❌ Player not found: {name}")
            continue

        href = link['href']
        match = re.search(r'/player/(\d+)/([^/]+)', href)
        if match:
            player_id, slug = match.groups()
            print(f"✅ Found → ID: {player_id}, Slug: {slug}")
            player_info_list.append({
                "name": name.strip(),
                "vlr_id": int(player_id),
                "slug": slug
            })
        else:
            print(f"❌ Failed to parse ID/slug for: {name}")

    return player_info_list

def get_all_match_links(player_id, player_slug):
    base_url = "https://www.vlr.gg"
    endpoint = f"/player/matches/{player_id}/{player_slug}/"
    match_links = []
    page = 1

    while True:
        url = f"{base_url}{endpoint}?page={page}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        cards = soup.select('a.wf-card.fc-flex.m-item')

        if not cards:
            break

        for card in cards:
            href = card.get('href')
            if href:
                full_url = base_url + href
                match_links.append(full_url)

        page += 1
        time.sleep(1)  # Be polite

    return match_links

def scrape_player_matches(player_names):
    if len(player_names) > 5:
        print("⚠️ Only the first 5 players will be processed.")
        player_names = player_names[:5]

    player_list = get_vlr_ids_for_players(player_names)
    output_dict = {}

    for player in player_list:
        print(f"\n🔗 Getting matches for {player['name']}...")
        matches = get_all_match_links(player['vlr_id'], player['slug'])
        print(f"✅ Found {len(matches)} matches for {player['name']}")

        output_dict[player["name"]] = {
            "links": matches
        }

    with open("player_match_links.json", "w", encoding="utf-8") as f:
        json.dump(output_dict, f, indent=4, ensure_ascii=False)

    print("\n📁 Match links saved to 'player_match_links.json'")

if __name__ == "__main__":
    raw_input_names = input("Enter up to 5 player names (comma-separated): ")
    name_list = [n.strip() for n in raw_input_names.split(",") if n.strip()]
    scrape_player_matches(name_list)
