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

        # Load data for entity recognition
        self.player_feats = load_player_features()
        self.agents = list(AGENT_ROLE_MAP.keys())
        self.maps = list(self.player_feats["map"].unique())

        # Setup Entity Ruler for domain-specific entities
        self.ruler = self.nlp.add_pipe("entity_ruler", before="ner")

        # Add Agents to ruler
        agent_patterns = [{"label": "AGENT", "pattern": agent} for agent in self.agents]
        # Add Maps to ruler
        map_patterns = [{"label": "MAP", "pattern": m} for m in self.maps]

        self.ruler.add_patterns(agent_patterns + map_patterns)

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
        if any(word in text for word in ["predict", "who wins", "vs", "match", "probability"]):
            return "MATCH_PREDICTION"
        if any(word in text for word in ["best agent", "what should", "optimize agent"]):
            return "AGENT_OPTIMIZATION"
        if any(word in text for word in ["counter", "stop", "beat"]):
            return "COUNTER_STRATEGY"
        if any(word in text for word in ["profile", "tell me about", "stats of"]):
            return "PLAYER_PROFILE"
        if any(word in text for word in ["build a team", "roster", "optimize team"]):
            return "TEAM_OPTIMIZATION"
        return "GENERAL_QUERY"

    def _filtered_find_best_counter(self, agent: str, map_name: str) -> Dict[str, Any]:
        """Wraps find_best_counter to restrict 'Miks'."""
        res = find_best_counter(agent, map_name)
        if res["agent"] == "Miks":
            # To actually find the NEXT best, we'd need to modify counter_logic.py
            # For now, we return a clear filtered message or "Unknown"
            return {"agent": "Unknown", "reason": "The top statistical counter was Miks, but he is restricted for pro-play consistency."}
        return res

    def handle_query(self, user_input: str) -> str:
        entities = self._extract_entities(user_input)
        intent = self._determine_intent(user_input)

        # Extract core components
        player = entities["players"][0] if entities["players"] else None
        agent = entities["agents"][0] if entities["agents"] else None
        map_name = entities["maps"][0] if entities["maps"] else "Bind" # Default to Bind

        if intent == "COUNTER_STRATEGY":
            if not agent:
                return "Which agent would you like me to find a counter for?"
            counter = self._filtered_find_best_counter(agent, map_name)
            return f"To counter {agent} on {map_name}, I recommend using {counter['agent']}. {counter['reason']}"

        elif intent == "AGENT_OPTIMIZATION":
            if not player:
                return "Which player are we optimizing for?"
            res = suggest_best_agent(player, map_name)
            if "error" in res: return res["error"]
            best = res["suggestions"][0]
            return f"The best agent for {player} on {map_name} is {best['agent']} with a predicted rating of {best['predicted_rating']}."

        elif intent == "PLAYER_PROFILE":
            if not player:
                return "Which player's profile do you want to see?"
            res = process_player_query(player)
            if "error" in res: return res["error"]
            return f"{player} is primarily a {res['main_role']} with an average rating of {res['average_stats']['rating']} and ACS of {res['average_stats']['acs']}."

        elif intent == "MATCH_PREDICTION":
            if len(entities["players"]) < 2:
                return "Please provide at least two players (one from each team) to predict a match."

            # Simple split: first half players vs second half
            mid = len(entities["players"]) // 2
            team_a_names = entities["players"][:mid]
            team_b_names = entities["players"][mid:]

            # Assign agents if found, otherwise default to Jett/Omen
            team_a = [{"name": p, "agent": agent if agent else "Omen"} for p in team_a_names]
            team_b = [{"name": p, "agent": agent if agent else "Fade"} for p in team_b_names]

            # Fill to 5 players for match prediction
            while len(team_a) < 5: team_a.append({"name": f"Fill{len(team_a)}", "agent": "Sova"})
            while len(team_b) < 5: team_b.append({"name": f"Fill{len(team_b)}", "agent": "Killjoy"})

            res = process_match_query(team_a, team_b, map_name)
            win_prob = res["team_a_win_probability"] * 100
            return f"Predicting {', '.join(team_a_names)} vs {', '.join(team_b_names)} on {map_name}... Team A has a {win_prob}% chance of winning. Confidence: {res['confidence']}."

        elif intent == "TEAM_OPTIMIZATION":
            if not entities["players"]:
                return "Which players should I include in the team optimization?"

            res = suggest_best_composition(entities["players"], map_name)
            if not res["compositions"]:
                return "Could not find an optimal composition for these players."

            best_comp = res["compositions"][0]
            comp_str = ", ".join([f"{p}: {a}" for p, a in best_comp["players"]])
            return f"The optimized composition for {map_name} is: {comp_str}. Total predicted team rating: {best_comp['total_rating']}."

        else:
            return "I'm not sure how to help with that. You can ask me to predict matches, suggest the best agent for a player, or find counters for specific agents!"
