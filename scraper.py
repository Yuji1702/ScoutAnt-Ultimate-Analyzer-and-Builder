import requests
from bs4 import BeautifulSoup
import json


def clean_text(text):
    """Clean and format text content"""
    return (
        text.strip()
        .replace('\xa0', ' ')
        .replace('\n', ' ')
        .replace('/', '')
        .replace('%', '')
        .strip()
    )

def extract_map_outcomes(soup, target_player_name):
    """Determines Win/Loss for each map by checking player location in first or second overview table"""
    outcomes = []
    target_clean = clean_text(target_player_name).lower()

    tables = soup.find_all('table', class_='wf-table-inset mod-overview')
    table_index = 0

    while table_index + 3 <= len(tables):  
        outcome = "Unknown"

        try:
            team1_table = tables[table_index]
            for row in team1_table.find('tbody').find_all('tr'):
                cell = row.find('td', class_='mod-player')
                if cell:
                    name_div = cell.find('div', class_='text-of')
                    if name_div and clean_text(name_div.text).lower() == target_clean:
                        outcome = "Win"
                        break

            if outcome == "Unknown":
                team2_table = tables[table_index + 3]
                for row in team2_table.find('tbody').find_all('tr'):
                    cell = row.find('td', class_='mod-player')
                    if cell:
                        name_div = cell.find('div', class_='text-of')
                        if name_div and clean_text(name_div.text).lower() == target_clean:
                            outcome = "Loss"
                            break

        except Exception:
            outcome = "Unknown"

        outcomes.append(outcome)
        table_index += 2  
    if outcomes:
        outcomes.insert(1, "All")
    return outcomes



def extract_map_names(soup):
    """Extracts valid map names from the match page navigation"""
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
    """Extracts player stats from match page, optionally filtered by player name"""
    try:
        response = requests.get(map_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        map_names = extract_map_names(soup)
        map_outcome = extract_map_outcomes(soup, target_player_name)
        map_names_for_stats = [m for m in map_names if m != "All"]
        map_outcome_for_stats = [m for m in map_outcome if m != "All"]
        print(map_outcome_for_stats)
        tables = soup.find_all('table', class_='wf-table-inset mod-overview')
        all_players = []
        cleaned_target = clean_text(target_player_name).lower() if target_player_name else None

        map_index = 0  
        outcome_index = 0
        for table_index, table in enumerate(tables):
            if table_index % 3 == 0 and table_index > 0:
                map_index += 1

            current_map = (
                map_names_for_stats[map_index]
                if map_index < len(map_names_for_stats)
                else f"Map-{map_index + 1}"
            )
            map_outcome = (
                map_outcome_for_stats[outcome_index]
                if outcome_index < len(map_outcome_for_stats)
                else f"Outcome-{outcome_index + 1}"
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
                        player_data['Outcome'] = map_outcome
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

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Processing error: {e}")
        return None

if __name__ == "__main__":
    
    map_url = "https://www.vlr.gg/487989/fut-esports-vs-team-vitality-esports-world-cup-2025-ubsf/?game=216874&tab=overview"
    
    target_player = "Derke"  
    
    stats = extract_map_stats(map_url, target_player_name=target_player)

    # response = requests.get(map_url)
    # response.raise_for_status()
    # soup = BeautifulSoup(response.content, 'html.parser')
    # maps = extract_map_names(soup)
    # print(maps)
    
    # response = requests.get(map_url)
    # response.raise_for_status()
    # soup = BeautifulSoup(response.content, 'html.parser')
    # outcomes = extract_map_outcomes(soup, target_player)
    # print(outcomes)


    if stats:
        print(json.dumps(stats, indent=4, ensure_ascii=False))
    else:
        print(f"No stats found for {target_player}")