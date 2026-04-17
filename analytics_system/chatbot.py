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

    def handle_query(self, user_input: str) -> Dict[str, Any]:
        entities = self._extract_entities(user_input)
        intent = self._determine_intent(user_input)

        # Extract core components
        player = entities["players"][0] if entities["players"] else None
        agent = entities["agents"][0] if entities["agents"] else None
        map_name = entities["maps"][0] if entities["maps"] else "Bind" # Default to Bind

        if intent == "COUNTER_STRATEGY":
            if not agent:
                return {"response": "Which agent would you like me to find a counter for?", "data": None}
            counter = self._filtered_find_best_counter(agent, map_name)
            return {"response": f"To counter {agent} on {map_name}, I recommend using {counter['agent']}. {counter['reason']}", "data": {"type": "counter", "analysis": counter}}

        elif intent == "AGENT_OPTIMIZATION":
            if not player:
                return {"response": "Which player are we optimizing for?", "data": None}
            res = suggest_best_agent(player, map_name)
            if "error" in res: return {"response": res["error"], "data": None}
            best = res["suggestions"][0]
            return {"response": f"The best agent for {player} on {map_name} is {best['agent']} with a predicted rating of {best['predicted_rating']}.", "data": {"type": "agent_optimization", "analysis": res}}

        elif intent == "PLAYER_PROFILE":
            if not player:
                return {"response": "Which player's profile do you want to see?", "data": None}
            res = process_player_query(player)
            if "error" in res: return {"response": res["error"], "data": None}
            return {"response": f"{player} is primarily a {res['main_role']} with an average rating of {res['average_stats']['rating']} and ACS of {res['average_stats']['acs']}.", "data": {"type": "player_profile", "analysis": res}}

        elif intent == "MATCH_PREDICTION":
            if len(entities["players"]) < 2:
                return {"response": "Please provide at least two players (one from each team) to predict a match. You can optionally specify their agents.", "data": None}

            # Simple split: first half players vs second half
            mid = len(entities["players"]) // 2
            team_a_names = entities["players"][:mid]
            team_b_names = entities["players"][mid:]

            # Map requested agents sequentially to all players found
            query_agents = entities["agents"]
            all_players = team_a_names + team_b_names
            player_agent_map = {}
            for i, p in enumerate(all_players):
                if i < len(query_agents):
                    player_agent_map[p] = query_agents[i]
                else:
                    player_agent_map[p] = "Omen" if i < mid else "Fade"

            team_a = [{"name": p, "agent": player_agent_map[p]} for p in team_a_names]
            team_b = [{"name": p, "agent": player_agent_map[p]} for p in team_b_names]

            # Teams are evaluated strictly based on provided names (e.g., 2v2, 3v3, 1v1)

            res = process_match_query(team_a, team_b, map_name)
            win_prob = res["team_a_win_probability"] * 100
            return {"response": f"Predicting {', '.join(team_a_names)} vs {', '.join(team_b_names)} on {map_name}... Team A has a {win_prob}% chance of winning. Confidence: {res['confidence']}.", "data": {"type": "match_prediction", "analysis": res}}

        elif intent == "TEAM_OPTIMIZATION":
            if not entities["players"]:
                return {"response": "Which players should I include in the team optimization?", "data": None}

            res = suggest_best_composition(entities["players"], map_name)
            if not res["compositions"]:
                return {"response": "Could not find an optimal composition for these players.", "data": None}

            best_comp = res["compositions"][0]
            comp_str = ", ".join([f"{p}: {a}" for p, a in best_comp["players"]])
            return {"response": f"The optimized composition for {map_name} is: {comp_str}. Total predicted team rating: {best_comp['total_rating']}.", "data": {"type": "team_optimization", "analysis": res}}

        else:
            return {"response": "I'm not sure how to help with that. You can ask me to predict matches, suggest the best agent for a player, or find counters for specific agents!", "data": None}
