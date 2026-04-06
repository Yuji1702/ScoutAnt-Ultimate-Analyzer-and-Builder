import json, sys

with open("match_stats_db.json", "r", encoding="utf-8") as f:
    data = json.load(f)

matches = data["matches"]
keys = list(matches.keys())

output = []
output.append(f"Total matches: {len(keys)}")

k = keys[0]
m = matches[k]
output.append(f"Key: {k}")
output.append(f"Map: {m['map']}")
output.append(f"Winner: {m['winner']}")
output.append(f"Teams: {m['team_a']} vs {m['team_b']}")

p = m["players"][0]
for field, val in p.items():
    output.append(f"  {field}: {repr(val)}")

# Second player for comparison
p2 = m["players"][5]
output.append("--- Player 6 ---")
for field, val in p2.items():
    output.append(f"  {field}: {repr(val)}")

all_maps = sorted(set(v["map"] for v in matches.values()))
output.append(f"Maps: {all_maps}")

all_agents = sorted(set(p.get("agent","?") for v in matches.values() for p in v["players"]))
output.append(f"Agents: {all_agents}")

with open("inspect_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Done - wrote inspect_result.txt")
