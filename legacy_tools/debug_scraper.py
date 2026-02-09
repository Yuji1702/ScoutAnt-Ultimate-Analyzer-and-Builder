import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://www.vlr.gg/312779/gen-g-vs-sentinels-champions-tour-2024-masters-madrid-gf"
print(f"Fetching {url}...")
r = requests.get(url, headers=HEADERS)
soup = BeautifulSoup(r.text, 'html.parser')

game_divs = soup.select('div.vm-stats-game')
for div in game_divs:
    game_id = div.get('data-game-id')
    print(f"Game ID: {game_id}")
    
    table = div.select_one('table.wf-table-inset.mod-overview')
    if table:
        # Get first agent image
        img = table.select_one('td.mod-agents img')
        if img:
            print(f"  First Agent: {img.get('title') or img.get('alt')}")
        else:
            print("  No Agent Found")
    else:
        print("  No Table Found")
