import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def explore_events():
    url = "https://www.vlr.gg/events/?tier=all&region=all&status=completed"
    print(f"Fetching {url}...")
    
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        events = soup.select('a.event-item')
        print(f"Found {len(events)} events.")
        
        if events:
            # First event
            event = events[0]
            href = event.get('href') # /event/2276/...
            print(f"Inspecting Event: {href}")
            
            full_url = "https://www.vlr.gg" + href
            explore_event_page(full_url)

    except Exception as e:
        print(f"Error: {e}")

def explore_event_page(url):
    print(f"\nFetching Event Page: {url}...")
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 1. Look for "Matches" tab
        tabs = soup.select('a.wf-nav-item')
        for tab in tabs:
            if "Matches" in tab.get_text():
                print(f"Found Matches Tab: {tab.get('href')}")
                # If explicit matches tab exists and is different, fetch it
                if tab.get('href') not in url:
                    match_tab_url = "https://www.vlr.gg" + tab.get('href')
                    explore_matches_tab(match_tab_url)
                    return

        # 2. If no tab or we are on it, look for match links directly
        # Match links usually start with digits /12345/
        links = soup.find_all('a', href=True)
        count = 0
        for a in links:
            href = a['href']
            # Match regex: /123456/team-vs-team (and NOT /event/)
            if re.match(r'^/\d+/[^/]+$', href):
                print(f"Potential Match: {href}")
                count += 1
                if count >= 5: break
                
        if count == 0:
            print("No match links found on main page.")

    except Exception as e:
        print(f"Error: {e}")

def explore_matches_tab(url):
    print(f"\nFetching Matches Tab: {url}...")
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        links = soup.find_all('a', href=True)
        count = 0
        for a in links:
            href = a['href']
            if re.match(r'^/\d+/[^/]+$', href):
                print(f"Potential Match: {href}")
                count += 1
                if count >= 5: break
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_events()
