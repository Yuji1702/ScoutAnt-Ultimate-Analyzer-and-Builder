import spacy
from spacy.pipeline import EntityRuler
from typing import List, Dict, Any, Optional
import pandas as pd

from .utils import load_player_features, AGENT_ROLE_MAP, ROLES
from .prediction import predict_player_performance, predict_match_outcome
from .analysis import process_match_query, process_player_query
from ml_pipeline.meta_analysis import get_top_agents_for_map
from ml_pipeline.counter_logic import find_best_counter, analyze_composition_weakness
from ml_pipeline.prediction import suggest_best_agent, suggest_best_composition

class ValorantChatbot:
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")

        # Lazy loaded attributes
        self._player_feats = None
        self._agents = None
        self._maps = None

        # Setup Entity Ruler for domain-specific entities (we need agent/map lists here for patterns)
        # We load player features now to ensure ALL known players are recognized by the AI
        self.player_feats = load_player_features()
        self.agents = list(AGENT_ROLE_MAP.keys())
        self.actual_maps = list(self.player_feats["map"].unique())
        
        # Merge static maps with actual maps for coverage
        self.maps = sorted(list(set(["Bind", "Haven", "Split", "Ascent", "Icebox", "Breeze", "Fracture", "Pearl", "Lotus", "Sunset", "Abyss"] + self.actual_maps)))
        player_names = list(self.player_feats["player_name"].unique())

        self.ruler = self.nlp.add_pipe("entity_ruler", before="ner")

        # Add Patterns
        agent_patterns = [{"label": "AGENT", "pattern": agent} for agent in self.agents]
        map_patterns = [{"label": "MAP", "pattern": m} for m in self.maps]
        player_patterns = [{"label": "PERSON", "pattern": p} for p in player_names]

        self.ruler.add_patterns(agent_patterns + map_patterns + player_patterns)

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        doc = self.nlp(text)
        entities = {
            "players": [],
            "agents": [],
            "maps": [],
            "intent": None
        }

        for ent in doc.ents:
            if ent.label_ == "AGENT":
                entities["agents"].append(ent.text)
            elif ent.label_ == "MAP":
                entities["maps"].append(ent.text)
            elif ent.label_ == "PERSON":
                entities["players"].append(ent.text)

        # Fallback for players: check Proper Nouns that aren't agents or maps
        for token in doc:
            if token.pos_ == "PROPN" and token.text not in self.agents and token.text not in self.maps:
                if token.text not in entities["players"]:
                    entities["players"].append(token.text)

        return entities

    def _determine_intent(self, text: str) -> str:
        text = text.lower()
        
        # Match Prediction: needs keywords like 'predict', 'match', or 'vs'
        if any(w in text for w in ["predict", "match", "probability"]) or " vs " in text:
            return "MATCH_PREDICTION"
        
        # Agent Optimization: keywords like 'best agent' or 'optimize' + 'agent'
        if "best agent" in text or ("optimize" in text and "agent" in text) or "what should" in text:
            return "AGENT_OPTIMIZATION"
            
        # Team Optimization: keywords like 'best team', 'optimize' + 'team', 'roster', 'build'
        if "best team" in text or ("optimize" in text and "team" in text) or any(w in text for w in ["roster", "build a team", "composition"]):
            return "TEAM_OPTIMIZATION"
            
        # Counter Strategy: 'counter', 'stop', 'beat'
        if any(w in text for w in ["counter", "stop", "beat"]):
            return "COUNTER_STRATEGY"
            
        # Player Profile: 'profile', 'stats', 'tell me about'
        if any(w in text for w in ["profile", "stats", "tell me about"]):
            return "PLAYER_PROFILE"
            
        return "GENERAL_QUERY"


    def _filtered_find_best_counter(self, agent: str, map_name: str) -> Dict[str, Any]:
        """Wraps find_best_counter to restrict 'Miks'."""
        res = find_best_counter(agent, map_name)
        if res["agent"] == "Miks":
            # To actually find the NEXT best, we'd need to modify counter_logic.py
            # For now, we return a clear filtered message or "Unknown"
            return {"agent": "Unknown", "reason": "The top statistical counter was Miks, but he is restricted for pro-play consistency."}
        return res

    def handle_query(self, user_input: str) -> Dict[str, Any]:
        # Ensure player_feats is used from self.player_feats (loaded in __init__)
        entities = self._extract_entities(user_input)
        intent = self._determine_intent(user_input)

        # Extract core components
        player = entities["players"][0] if entities["players"] else None
        agent = entities["agents"][0] if entities["agents"] else None
        map_name = entities["maps"][0] if entities["maps"] else "Bind" # Default to Bind

        result = {
            "response": "",
            "data": None
        }

        if intent == "COUNTER_STRATEGY":
            if not agent:
                result["response"] = "Which agent would you like me to find a counter for?"
                return result
            
            counter = self._filtered_find_best_counter(agent, map_name)
            
            # Enrich with chart data: Win rates for comparison
            # We get the counter's win rate vs the opponent
            from ml_pipeline.meta_analysis import get_agent_vs_agent_win_rate
            win_rate_vs = get_agent_vs_agent_win_rate(counter["agent"], agent)
            
            result["response"] = f"To counter {agent} on {map_name}, I recommend using {counter['agent']}. {counter['reason']}"
            result["data"] = {
                "type": "counter",
                "analysis": {
                    "agent": counter["agent"],
                    "target_agent": agent,
                    "map": map_name,
                    "win_rate_vs": round(win_rate_vs, 1),
                    "reason": counter["reason"],
                    "strategic_steps": [
                        f"Pick {counter['agent']} to exploit {agent}'s specific weaknesses on {map_name}.",
                        "Coordinate with teammates to force engagements where your utility overlaps.",
                        "Focus on controlling key areas of the map where the counter is most effective."
                    ]
                }
            }

        elif intent == "AGENT_OPTIMIZATION":
            if not player:
                result["response"] = "Which player are we optimizing for?"
                return result
            
            res = suggest_best_agent(player, map_name)
            if "error" in res:
                result["response"] = res["error"]
                return result
                
            best = res["suggestions"][0]
            result["response"] = f"The best agent for {player} on {map_name} is {best['agent']} with a predicted rating of {best['predicted_rating']}."
            result["data"] = {
                "type": "agent_optimization",
                "analysis": {
                    "player": player,
                    "map": map_name,
                    "suggestions": res["suggestions"],
                    "strategic_steps": [
                        f"Master the '{best['agent']}' utility set specifically for {map_name} geometry.",
                        "Align your playstyle with the team's overall composition goals.",
                        "Practice individual site-hold or entry paths relevant to this agent-map combo."
                    ]
                }
            }

        elif intent == "PLAYER_PROFILE":
            if not player:
                result["response"] = "Which player's profile do you want to see?"
                return result
                
            res = process_player_query(player)
            if "error" in res:
                result["response"] = res["error"]
                return result
                
            result["response"] = f"{player} is primarily a {res['main_role']} with an average rating of {res['average_stats']['rating']} and ACS of {res['average_stats']['acs']}."
            
            # Align data with PlayerProfileDisplay.tsx expectations
            role_breakdown = {}
            if "role_performance" in res:
                total_rating = sum(res["role_performance"].values())
                if total_rating > 0:
                    role_breakdown = {k: v / total_rating for k, v in res["role_performance"].items()}

            result["data"] = {
                "type": "player_profile",
                "analysis": {
                    "player": player,
                    "main_role": res["main_role"],
                    "average_stats": res["average_stats"],
                    "role_breakdown": role_breakdown,
                    "agent_performance": res["agent_performance"],
                    "strengths": res["strengths"],
                    "weaknesses": res["weaknesses"]
                }
            }

        elif intent == "MATCH_PREDICTION":
            if len(entities["players"]) < 2:
                result["response"] = "Please provide at least two players (one from each team) to predict a match."
                return result

            mid = len(entities["players"]) // 2
            team_a_names = entities["players"][:mid]
            team_b_names = entities["players"][mid:]

            agents_list = entities["agents"]
            
            def build_team(names):
                team = []
                for i, p in enumerate(names):
                    a = agents_list.pop(0) if agents_list else ( "Omen" if i % 2 == 0 else "Jett" )
                    team.append({"name": p, "agent": a})
                return team

            team_a = build_team(team_a_names)
            team_b = build_team(team_b_names)

            res = process_match_query(team_a, team_b, map_name)
            win_prob = res["team_a_win_probability"] * 100
            result["response"] = f"Predicting {', '.join(team_a_names)} vs {', '.join(team_b_names)} on {map_name}... Team A has a {win_prob:.1f}% chance of winning."
            
            # Add strategic steps to reasoning
            res["strategic_roadmap"] = [
                "Early Game: Focus on securing orb control with initiator utility.",
                "Mid Round: Use controller smokes to isolate 1v1 engagements for your top fraggers.",
                "Late Game: Play for post-plant numbers using defensive utility."
            ]
            
            result["data"] = {
                "type": "match_prediction",
                "analysis": res
            }

        elif intent == "TEAM_OPTIMIZATION":
            if not entities["players"]:
                result["response"] = "Which players should I include in the team optimization?"
                return result

            res = suggest_best_composition(entities["players"], map_name)
            if not res["compositions"]:
                result["response"] = "Could not find an optimal composition for these players."
                return result

            best_comp = res["compositions"][0]
            comp_str = ", ".join([f"{p}: {a}" for p, a in best_comp["players"]])
            result["response"] = f"The optimized composition for {map_name} is: {comp_str}."
            result["data"] = {
                "type": "team_optimization",
                "analysis": {
                    "map": map_name,
                    "compositions": res["compositions"],
                    "strategic_roadmap": [
                        "Draft Phase: Prioritize the recommended comfort picks discovered by the AI.",
                        "Team Dynamic: Focus communications around the core initiator discovered for intel.",
                        "Execution: Apply the map-specific strategy steps in your practice sessions."
                    ]
                }
            }

        else:
            result["response"] = "I'm not sure how to help with that. You can ask me to predict matches, suggest the best agent for a player, or find counters for specific agents!"

        return result


        return result