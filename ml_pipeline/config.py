"""
config.py — Central configuration for the ScoutAnt ML pipeline.

Contains agent-to-role mappings, stat field definitions, file paths,
and constants used across all pipeline stages.
"""

import os

# ─── Paths ───────────────────────────────────────────────────────────────────

# Base directory is the project root (parent of ml_pipeline/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DB_PATH = os.path.join(BASE_DIR, "match_stats_db.json")

# Output directory for cleaned data & models
DATA_DIR = os.path.join(BASE_DIR, "ml_pipeline", "data")
MODEL_DIR = os.path.join(BASE_DIR, "ml_pipeline", "models")

PLAYER_STATS_PARQUET = os.path.join(DATA_DIR, "player_stats.parquet")
PLAYER_FEATURES_PARQUET = os.path.join(DATA_DIR, "player_features.parquet")
MATCH_FEATURES_PARQUET = os.path.join(DATA_DIR, "match_features.parquet")

PLAYER_MODEL_PATH = os.path.join(MODEL_DIR, "player_performance_rf.pkl")
MATCH_MODEL_PATH = os.path.join(MODEL_DIR, "match_win_predictor.pkl")

# ─── Agent → Role Mapping ───────────────────────────────────────────────────

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

    # Initiators
    "Sova":       "Initiator",
    "Fade":       "Initiator",
    "Skye":       "Initiator",
    "Breach":     "Initiator",
    "Kayo":       "Initiator",   # stored as "Kayo" in DB (not KAY/O)
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

# ─── Stat Fields ─────────────────────────────────────────────────────────────

# Fields that come as "total attack defense" strings
STAT_FIELDS = ["rating", "acs", "k", "d", "a", "kd_diff", "kast", "adr", "hs_percent", "fk", "fd"]

# The three phases each stat is split into
PHASES = ["total", "attack", "defense"]

# ─── Bad Data Filters ────────────────────────────────────────────────────────

BAD_AGENTS = {"Unknown", "Miks", "95b78ed7-4637-86d9-7"}
BAD_MAPS = {"N/A", "TBD"}

# ─── Feature Column Names (generated during feature engineering) ─────────────

# These are the expanded column names from the stat fields
# e.g., "k" → "kills_total", "kills_attack", "kills_defense"
STAT_COLUMN_MAP = {
    "k":          "kills",
    "d":          "deaths",
    "a":          "assists",
    "kd_diff":    "kd_diff",
    "rating":     "rating",
    "acs":        "acs",
    "kast":       "kast",
    "adr":        "adr",
    "hs_percent": "hs_pct",
    "fk":         "first_kills",
    "fd":         "first_deaths",
}
