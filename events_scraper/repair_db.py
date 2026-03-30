import os
import json

def repair_db(db_path):
    if not os.path.exists(db_path):
        print(f"❌ File not found: {db_path}")
        return

    print(f"🛠️ Repairing {db_path}...")
    
    with open(db_path, "rb") as f:
        content = f.read()

    # Find the last occurrence of a closing brace for a match object
    # The structure is: "unique_id": { ... }
    # Each match object ends with "        }" (8 spaces + brace)
    last_brace = content.rfind(b"\n        }")
    
    if last_brace == -1:
        print("❌ Could not find a valid match entry end.")
        return

    # Keep content up to the closing brace of the last match
    # Structure:
    # {
    #     "matches": {
    #         "id1": { ... },
    #         "id2": { ... }
    #     }
    # }
    
    # We want to find the brace, then check if it's followed by a comma or not.
    # If it's the last one being written, it might or might not have a comma.
    
    # Let's take up to the brace + the newline
    new_content = content[:last_brace + 10].rstrip()
    
    # Strip trailing comma if it was in the middle of writing the next one
    if new_content.endswith(b","):
        new_content = new_content[:-1]
    
    # Add closing braces
    new_content += b"\n    }\n}"
    
    backup_path = db_path + ".bak"
    os.rename(db_path, backup_path)
    print(f"📦 Backup created at {backup_path}")
    
    with open(db_path, "wb") as f:
        f.write(new_content)
    
    print(f"✅ Repaired {db_path}")
    
    # Verify
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"📊 Verification successful! DB now has {len(data.get('matches', {}))} matches.")
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "match_stats_db.json")
    repair_db(db_file)
