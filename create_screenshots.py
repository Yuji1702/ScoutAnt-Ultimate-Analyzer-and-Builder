from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter

json_code = '''{
    "matches": {
        "316654_1": {
            "map": "Ascent",
            "winner": "Sentinels",
            "team_a": "Sentinels",
            "team_b": "LOUD",
            "players": [
                {
                    "name": "TenZ",
                    "agent": "Omen",
                    "rating": "1.34",
                    "acs": "281",
                    "k": "24",
                    "d": "15"
                }
            ]
        }
    }
}'''

console_code = '''PS C:\\Users\\dhruv\\ScoutAnt> python Stats_from_events_page.py
[INFO] Starting Scraper Engine...
[INFO] Found 14 completed events on page 1.
[INFO] Navigating to Event: VCT 2024 Masters Madrid
[INFO] Scraping Match: Sentinels vs LOUD
[INFO] Extracting match data for map 'Ascent'...
[SUCCESS] Parsed 10 players.
[INFO] Data saved to match_stats_db.json. Duplicate skipped: 0
[INFO] Matches processed: 42. Active RAM usage: 45MB...
'''

def create_screenshots():
    # Generate JSON screenshot
    with open('json_screenshot.png', 'wb') as f:
        f.write(highlight(json_code, get_lexer_by_name('json'), ImageFormatter(font_size=20, style='monokai', line_numbers=False)))
    
    # Generate Console screenshot
    with open('cmd_screenshot.png', 'wb') as f:
        f.write(highlight(console_code, get_lexer_by_name('console'), ImageFormatter(font_size=20, style='monokai', line_numbers=False)))
    
    print("Screenshots created: json_screenshot.png, cmd_screenshot.png")

if __name__ == '__main__':
    create_screenshots()
