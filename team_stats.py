import json
import os
from scraper import extract_map_stats  # Your scraping function

def scrape_all_team_stats(player_links_file, output_file="team_player_stats.json"):
    # Load existing stats file
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            full_data = json.load(f)
    else:
        full_data = {}

    # Load player match links
    with open(player_links_file, "r", encoding="utf-8") as f:
        player_links = json.load(f)

    for player_name, info in player_links.items():
        print(f"\n📊 Scraping stats for {player_name}...")

        player_entry = full_data.get(player_name, {"stats": [], "processed_links": []})
        existing_links = set(player_entry["processed_links"])
        new_stats = player_entry["stats"]

        for url in info["links"]:
            if url in existing_links:
                print(f"⏩ Skipping (already processed): {url}")
                continue

            print(f"🔗 Scraping: {url}")
            try:
                stats = extract_map_stats(url, target_player_name=player_name)

                if stats:
                    for entry in stats:
                        entry["match_link"] = url  # Attach the URL to the stat
                    new_stats.extend(stats)
                    player_entry["processed_links"].append(url)
                else:
                    print(f"⚠️ No stats found for {player_name} in {url}")

            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")

            # Save after each link
            full_data[player_name] = {
                "stats": new_stats,
                "processed_links": player_entry["processed_links"]
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(full_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Finished {player_name}, total matches: {len(player_entry['processed_links'])}")

    print("\n💾 All available player stats saved.")

if __name__ == "__main__":
    scrape_all_team_stats("player_match_links.json")
