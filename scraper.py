import requests
from bs4 import BeautifulSoup
import json
import time

# === UTILITY FUNCTIONS ===
def clean_text(text):
    return (
        text.strip()
        .replace('\xa0', ' ')
        .replace('\n', ' ')
        .replace('/', '')
        .replace('%', '')
        .strip()
    )

def extract_map_names(soup):
    valid_map_names = []
    map_nav_items = soup.select('div.vm-stats-gamesnav > div')
    for item in map_nav_items:
        if item.get('data-game-id') == 'all' or 'mod-disabled' in item.get('class', []):
            continue
        inner_divs = item.find_all('div', recursive=False)
        for div in inner_divs:
            if not div.get('class'):
                span = div.find('span')
                if span:
                    span.extract()
                map_name = clean_text(div.get_text())
                if map_name:
                    valid_map_names.append(map_name)
                break
    if valid_map_names:
        valid_map_names.insert(1, "All")
    return valid_map_names

def extract_map_stats(map_url, target_player_name=None):
    try:
        response = requests.get(map_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        map_names = extract_map_names(soup)
        map_names_for_stats = [m for m in map_names if m != "All"]

        tables = soup.find_all('table', class_='wf-table-inset mod-overview')
        all_players = []
        cleaned_target = clean_text(target_player_name).lower() if target_player_name else None
        map_index = 0

        for table_index, table in enumerate(tables):
            if table_index % 3 == 0 and table_index > 0:
                map_index += 1

            current_map = (
                map_names_for_stats[map_index]
                if map_index < len(map_names_for_stats)
                else f"Map-{map_index + 1}"
            )

            headers = [clean_text(th.text) for th in table.find('thead').find_all('th')]
            for row in table.find('tbody').find_all('tr'):
                player_data = {}
                cells = row.find_all('td')

                for header, cell in zip(headers, cells):
                    if 'mod-player' in cell.get('class', []):
                        name_div = cell.find('div', class_='text-of')
                        player_data['Player'] = clean_text(name_div.text) if name_div else 'Unknown'
                        player_data['Map'] = current_map
                        team_div = cell.find('div', class_='ge-text-light')
                        player_data['Team'] = clean_text(team_div.text) if team_div else 'Unknown'
                    elif 'mod-agents' in cell.get('class', []):
                        img = cell.find('img')
                        player_data['Agent'] = img['alt'] if img else 'N/A'
                    else:
                        raw_value = clean_text(cell.text)
                        values = [v.strip() for v in raw_value.split() if v.strip()]
                        if len(values) == 3:
                            player_data[header] = {
                                "All": values[0],
                                "Attack": values[1],
                                "Defense": values[2]
                            }
                        else:
                            player_data[header] = raw_value

                if player_data.get('Player') and player_data.get('Agent'):
                    if cleaned_target:
                        current_name = player_data['Player'].lower()
                        if current_name == cleaned_target:
                            all_players.append(player_data)
                    else:
                        all_players.append(player_data)

        if len(all_players) > 1:
            del all_players[1]

        return all_players

    except Exception as e:
        print(f"❌ Error processing {map_url}: {e}")
        return None

# === MAIN PIPELINE ===
def extract_all_stats(json_path="player_match_links.json", output_path="player_map_agent_stats.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            players = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return

    all_results = []

    for player in players:
        name = player['name']
        match_urls = player.get("matches", [])
        print(f"\n🎯 Extracting data for {name} ({len(match_urls)} matches)...")

        for i, url in enumerate(match_urls, 1):
            print(f"  🔍 [{i}/{len(match_urls)}] {url}")
            try:
                stats = extract_map_stats(url, target_player_name=name)
                if stats:
                    all_results.extend(stats)
                time.sleep(1.2)  # polite delay
            except Exception as e:
                print(f"    ❌ Skipping due to error: {e}")

    # ✅ Save output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"\n✅ All stats saved to '{output_path}'")


if __name__ == "__main__":
    extract_all_stats()