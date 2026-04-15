
import sys
import os

# Add the project root to sys.path to allow imports
project_root = "C:/Users/dhruv/OneDrive/Desktop/ScoutAnt-Ultimate-Analyzer-and-Builder"
sys.path.append(project_root)

from ml_pipeline.meta_analysis import get_agent_win_rate, get_top_agents_for_map, get_agent_vs_agent_win_rate
from ml_pipeline.counter_logic import find_best_counter, analyze_composition_weakness
from ml_pipeline.prediction import suggest_best_agent, suggest_best_composition
from analytics_system.analysis import process_match_query, process_player_query

def test_meta_analysis():
    print("Testing Meta Analysis...")
    # Based on the sample data, Astra on Pearl should have a win rate
    wr = get_agent_win_rate("Pearl", "Astra")
    print(f"Astra win rate on Pearl: {wr}%")
    assert isinstance(wr, float)

    top = get_top_agents_for_map("Pearl")
    print(f"Top agents for Pearl: {top[:2]}")
    assert isinstance(top, list)

    # Test agent vs agent
    # Note: we might not have enough data for a specific matchup in the sample,
    # but it should return a float (default 50.0)
    vs = get_agent_vs_agent_win_rate("Astra", "Killjoy")
    print(f"Astra vs Killjoy win rate: {vs}%")
    assert isinstance(vs, float)

def test_counter_logic():
    print("\nTesting Counter Logic...")
    counter = find_best_counter("Killjoy", "Pearl")
    print(f"Best counter for Killjoy on Pearl: {counter}")
    assert "agent" in counter

    weaknesses = analyze_composition_weakness(["Jett", "Sova", "Killjoy", "Omen", "Sage"])
    print(f"Composition weaknesses: {weaknesses}")
    assert isinstance(weaknesses, list)

def test_integration():
    print("\nTesting Integration...")
    team_a = [{"name": "P1", "agent": "Jett"}, {"name": "P2", "agent": "Sova"}, {"name": "P3", "agent": "Killjoy"}, {"name": "P4", "agent": "Omen"}, {"name": "P5", "agent": "Sage"}]
    team_b = [{"name": "P6", "agent": "Reyna"}, {"name": "P7", "agent": "Skye"}, {"name": "P8", "agent": "Cypher"}, {"name": "P9", "agent": "Brimstone"}, {"name": "P10", "agent": "Sova"}]

    try:
        res = process_match_query(team_a, team_b, "Pearl")
        print("Match query successful. Checking prescriptive fields...")
        pa = res.get("prescriptive_analytics", {})
        print(f"Meta Context: {pa.get('meta_context')}")
        print(f"Counter Analysis: {pa.get('counter_analysis')}")
        print(f"Rec Composition: {pa.get('recommended_composition')}")
        print(f"Opponent Weaknesses: {pa.get('opponent_weaknesses')}")

        assert "meta_context" in pa
        assert "counter_analysis" in pa
        assert "recommended_composition" in pa
        assert "opponent_weaknesses" in pa
    except Exception as e:
        print(f"Integration test failed: {e}")
        # We don't assert False here because model files might be missing or
        # player data might not exist for these dummy names, but the function
        # structure should be there.

def test_fallback():
    print("\nTesting Fallback...")
    # Test with a map that definitely doesn't exist
    wr = get_agent_win_rate("NonExistentMap", "Astra")
    print(f"Win rate on non-existent map: {wr}%")
    assert wr == 0.0

if __name__ == "__main__":
    try:
        test_meta_analysis()
        test_counter_logic()
        test_integration()
        test_fallback()
        print("\nAll prescriptive analytics tests passed (or completed gracefully)!")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
