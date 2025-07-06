import json
from scraper import extract_map_stats  # Import your function

def scrape_all_team_stats(player_links_file):
    with open(player_links_file, "r", encoding="utf-8") as f:
        player_links = json.load(f)

    full_data = {}

    for player_name, info in player_links.items():
        print(f"\n📊 Scraping stats for {player_name}...")
        player_data = []

        for url in info["links"]:
            print(f"🔗 URL: {url}")
            stats = extract_map_stats(url, target_player_name=player_name)

            if stats:
                player_data.extend(stats)
            else:
                print(f"⚠️ No data found for {player_name} in {url}")

        full_data[player_name] = player_data

    # Save all scraped stats
    with open("team_player_stats.json", "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)

    print("\n✅ All player stats saved to 'team_player_stats.json'")

if __name__ == "__main__":
    scrape_all_team_stats("player_match_links.json")
