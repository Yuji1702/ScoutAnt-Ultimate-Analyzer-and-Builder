import os
import pandas as pd
import joblib

# Paths to models and data inside ml_pipeline
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml_pipeline", "models")
DATA_DIR = os.path.join(BASE_DIR, "ml_pipeline", "data")

PLAYER_MODEL_PATH = os.path.join(MODEL_DIR, "player_performance_rf.pkl")
MATCH_MODEL_PATH = os.path.join(MODEL_DIR, "match_win_predictor.pkl")
PLAYER_FEATURES_PARQUET = os.path.join(DATA_DIR, "player_features.parquet")
MATCH_FEATURES_PARQUET = os.path.join(DATA_DIR, "match_features.parquet")

AGENT_ROLE_MAP = {
    # Duelists
    "Jett":       "Duelist",
    "Raze":       "Duelist",
    "Neon":       "Duelist",
    "Reyna":      "Duelist",
    "Yoru":       "Duelist",
    "Phoenix":    "Duelist",
    "Iso":        "Duelist",
    "Waylay":     "Duelist",

    # Controllers
    "Astra":      "Controller",
    "Omen":       "Controller",
    "Viper":      "Controller",
    "Brimstone":  "Controller",
    "Harbor":     "Controller",
    "Clove":      "Controller",
    "Miks":       "Controller", # user provided

    # Initiators
    "Sova":       "Initiator",
    "Fade":       "Initiator",
    "Skye":       "Initiator",
    "Breach":     "Initiator",
    "Kayo":       "Initiator",
    "KAY/O":      "Initiator",
    "Gekko":      "Initiator",
    "Tejo":       "Initiator",

    # Sentinels
    "Killjoy":    "Sentinel",
    "Cypher":     "Sentinel",
    "Sage":       "Sentinel",
    "Chamber":    "Sentinel",
    "Deadlock":   "Sentinel",
    "Vyse":       "Sentinel",
    "Veto":       "Sentinel",
}

ROLES = ["Duelist", "Controller", "Initiator", "Sentinel"]

# Simple in-memory cache to avoid reading parquet/pickle files on every request
_CACHE = {}

def load_player_model():
    if "player_model" not in _CACHE:
        _CACHE["player_model"] = joblib.load(PLAYER_MODEL_PATH)
    return _CACHE["player_model"]

def load_match_model():
    if "match_model" not in _CACHE:
        _CACHE["match_model"] = joblib.load(MATCH_MODEL_PATH)
    return _CACHE["match_model"]

def load_player_features() -> pd.DataFrame:
    if "player_feats" not in _CACHE:
        _CACHE["player_feats"] = pd.read_parquet(PLAYER_FEATURES_PARQUET)
    return _CACHE["player_feats"]

def load_match_features() -> pd.DataFrame:
    if "match_feats" not in _CACHE:
        _CACHE["match_feats"] = pd.read_parquet(MATCH_FEATURES_PARQUET)
    return _CACHE["match_feats"]

def get_role_for_agent(agent_name: str) -> str:
    return AGENT_ROLE_MAP.get(agent_name, "Unknown")
