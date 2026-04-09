# ScoutAnt — Complete System Documentation

> A Valorant match-data analyzer and team-building assistant powered by web scraping, data engineering, and machine learning.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Project Structure](#2-project-structure)
3. [Installation & Setup](#3-installation--setup)
4. [Module Reference](#4-module-reference)
   - [4.1 `events_scraper/` — Data Collection](#41-events_scraper--data-collection)
   - [4.2 `ml_pipeline/` — ML Data Pipeline](#42-ml_pipeline--ml-data-pipeline)
   - [4.3 `analytics_system/` — Analytics & Prediction API](#43-analytics_system--analytics--prediction-api)
   - [4.4 `legacy_tools/` — Legacy / Utility Scripts](#44-legacy_tools--legacy--utility-scripts)
   - [4.5 Root-Level Files](#45-root-level-files)
5. [Data Flow: End-to-End Pipeline](#5-data-flow-end-to-end-pipeline)
6. [Frontend Integration Guide](#6-frontend-integration-guide)
   - [6.1 Primary Entry Points](#61-primary-entry-points)
   - [6.2 API Contracts (Input → Output)](#62-api-contracts-input--output)
     - [Match Query](#match-query-process_match_query)
     - [Player Profile Query](#player-profile-query-process_player_query)
     - [Player Performance Prediction](#player-performance-prediction-predict_player)
     - [Match Win Prediction](#match-win-prediction-predict_match)
     - [Team Simulation](#team-simulation-simulate_team)
     - [Agent Suggestion](#agent-suggestion-suggest_best_agent)
     - [Composition Suggestion](#composition-suggestion-suggest_best_composition)
   - [6.3 Wrapping in a Web API (Flask / FastAPI example)](#63-wrapping-in-a-web-api-flask--fastapi-example)
7. [CLI Reference](#7-cli-reference)
8. [Data Files Reference](#8-data-files-reference)
9. [Configuration Reference](#9-configuration-reference)

---

## 1. System Overview

ScoutAnt ingests professional Valorant match data from [vlr.gg](https://www.vlr.gg), processes it through a machine-learning pipeline, and exposes high-level analytics functions that a frontend (web app, dashboard, Discord bot, etc.) can call.

The system has three logical layers:

```
┌────────────────────────────────────────────────────┐
│  Layer 1 — DATA COLLECTION (events_scraper/)       │
│  Scrapes vlr.gg for match stats → match_stats_db   │
└──────────────────────┬─────────────────────────────┘
                       │ match_stats_db.json
┌──────────────────────▼─────────────────────────────┐
│  Layer 2 — ML PIPELINE (ml_pipeline/)              │
│  Clean → Feature Engineer → Train → .pkl models   │
└──────────────────────┬─────────────────────────────┘
                       │ .parquet features + .pkl models
┌──────────────────────▼─────────────────────────────┐
│  Layer 3 — ANALYTICS API (analytics_system/)       │
│  Python functions callable from any frontend       │
└────────────────────────────────────────────────────┘
```

---

## 2. Project Structure

```
ScoutAnt-Ultimate-Analyzer-and-Builder/
│
├── analytics_system/            # ← PRIMARY API FOR FRONTEND
│   ├── __init__.py
│   ├── analysis.py              # High-level query handlers
│   ├── prediction.py            # ML model inference wrappers
│   └── utils.py                 # Model/data loaders, agent-role map, cache
│
├── ml_pipeline/                 # ML data pipeline (run once to rebuild models)
│   ├── __init__.py
│   ├── config.py                # All paths, constants, agent→role mapping
│   ├── data_cleaning.py         # Step 1: JSON → cleaned parquet
│   ├── feature_engineering.py   # Step 2: cleaned → player & match features
│   ├── model_training.py        # Step 3: features → trained .pkl models
│   ├── prediction.py            # Step 4: inference + agent/comp suggestions
│   ├── run_pipeline.py          # CLI orchestrator for the entire pipeline
│   ├── data/                    # Generated feature files (parquet)
│   │   ├── player_stats.parquet
│   │   ├── player_features.parquet
│   │   └── match_features.parquet
│   └── models/                  # Trained model files
│       ├── player_performance_rf.pkl
│       └── match_win_predictor.pkl
│
├── events_scraper/              # Web scraper — builds match_stats_db.json
│   ├── Stats_from_events_page.py  # Main bulk event crawler
│   ├── analyzer.py              # Meta-composition analyzer (uses raw DB)
│   └── repair_db.py             # Repairs a truncated JSON database
│
├── legacy_tools/                # Older/utility scripts (not production path)
│   ├── scraper.py               # Single-match detailed stat extractor
│   ├── scraper_v2.py            # Agent-only scraper (leaner DB format)
│   ├── team_stats.py            # Batch scraper driven by player_match_links.json
│   ├── player_links.py          # Fetches all match URLs for given player names
│   ├── debug_scraper.py         # One-off debug script for vlr.gg page structure
│   └── event_explorer.py        # One-off script to explore vlr.gg events listing
│
├── match_stats_db.json          # Raw scraped match database
├── requirements.txt             # Python dependencies
├── test_system.py               # Quick integration test for analytics_system
├── check_columns.py             # Utility: prints parquet column names
├── inspect_data.py              # Utility: data inspection helper
├── verify_clean.py              # Utility: verifies clean pipeline output
├── inspect_output.txt           # Output of inspect_data.py
├── inspect_result.txt           # Output of data inspection
├── ml_pipeline_clean_log.txt    # Log from a previous pipeline run
├── verify_clean_output.txt      # Output of verify_clean.py
└── README.md                    # Project overview
```

---

## 3. Installation & Setup

```bash
git clone https://github.com/Yuji1702/ScoutAnt-Ultimate-Analyzer-and-Builder.git
cd ScoutAnt-Ultimate-Analyzer-and-Builder
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`):

| Package | Purpose |
|---|---|
| `requests` | HTTP requests for web scraping |
| `beautifulsoup4` | HTML parsing of vlr.gg pages |
| `pandas >= 2.0` | DataFrames for data processing |
| `numpy >= 1.24` | Numerical operations |
| `scikit-learn >= 1.3` | ML models & preprocessing pipelines |
| `xgboost >= 2.0` | Available for model upgrades (not yet used) |
| `pyarrow >= 14.0` | Parquet file read/write |
| `joblib >= 1.3` | Model serialisation/deserialisation |

### First-time pipeline run

If you have a populated `match_stats_db.json`, run the full pipeline:

```bash
python -m ml_pipeline.run_pipeline --step all
```

This will:
1. Clean the raw JSON → `ml_pipeline/data/player_stats.parquet`
2. Engineer features → `player_features.parquet` + `match_features.parquet`
3. Train models → `player_performance_rf.pkl` + `match_win_predictor.pkl`

---

## 4. Module Reference

---

### 4.1 `events_scraper/` — Data Collection

#### `Stats_from_events_page.py`

**Purpose:** The primary bulk web scraper. Crawls **all completed events** on vlr.gg across all pages, follows event links to collect all match URLs, scrapes per-map player statistics from each match, and appends them to `match_stats_db.json`.

**Key functions:**

| Function | Input | Output / Side Effect |
|---|---|---|
| `get_completed_events_all_pages(start_page=1)` | Starting page number (int) | `list[str]` — full event URLs |
| `get_matches_from_event(event_url)` | A vlr.gg event page URL | `list[str]` — match URLs found on that event page |
| `parse_stats_row(row)` | A BeautifulSoup `<tr>` element | `dict` with player stats (`name`, `agent`, `rating`, `acs`, `k`, `d`, `a`, `kast`, `adr`, `hs_percent`, `fk`, `fd`) or `None` |
| `scrape_match_detailed(match_url, db)` | Match URL, current DB dict | Updates `db["matches"]` in-place; skips already-seen match IDs |
| `load_db()` | *(none)* | `dict` — existing DB or `{"matches": {}}` |
| `save_db(data)` | DB dict | Writes to `match_stats_db.json` |
| `main()` | *(none — run as script)* | Populates `match_stats_db.json` with all scraped data |

**DB output format per match entry:**
```json
"matchId_gameId": {
  "map": "Bind",
  "winner": "Team Name",
  "team_a": "Team A Name",
  "team_b": "Team B Name",
  "players": [
    {
      "name": "TenZ",
      "agent": "Jett",
      "team": "Team A Name",
      "rating": "1.32",
      "acs": "287",
      "k": "22",
      "d": "14",
      "a": "5",
      "kd_diff": "+8",
      "kast": "78%",
      "adr": "160",
      "hs_percent": "34%",
      "fk": "4",
      "fd": "1"
    }
  ]
}
```

**Run:**
```bash
python events_scraper/Stats_from_events_page.py
```

---

#### `analyzer.py`

**Purpose:** A standalone analysis module that queries the raw `match_stats_db.json` directly (no ML). Provides meta-composition win-rate analysis and simple statistical player predictions.

**Key functions:**

| Function | Input | Output |
|---|---|---|
| `get_meta_compositions(map_name, top_n=5)` | `map_name: str`, `top_n: int` | `list[dict]` — top N winning agent compositions sorted by win rate |
| `predict_match(player_name, map_name, agent)` | player name, map, agent (all `str`) | `dict` with `avg_acs`, `avg_kills`, `avg_deaths`, `samples` — or `{"error": ...}` |

**`get_meta_compositions` output example:**
```json
[
  {
    "agents": ["Jett", "Killjoy", "Omen", "Skye", "Sova"],
    "wins": 12,
    "matches": 15,
    "win_rate": 80.0
  }
]
```

**`predict_match` output example:**
```json
{
  "prediction": {
    "player": "TenZ",
    "map": "Bind",
    "agent": "Jett",
    "avg_acs": 285.3,
    "avg_kills": 21.5,
    "avg_deaths": 13.2,
    "samples": 8
  }
}
```

---

#### `repair_db.py`

**Purpose:** Repairs a truncated or partially-written `match_stats_db.json` (e.g. after a crash mid-write). Finds the last complete match entry, strips incomplete data, and adds correct closing braces to produce valid JSON. Creates a `.bak` backup before modifying.

**Run:**
```bash
python events_scraper/repair_db.py
```

---

### 4.2 `ml_pipeline/` — ML Data Pipeline

The ML pipeline is run **once** (or whenever new scrape data is available) to rebuild models. It consists of four sequential steps.

---

#### `config.py`

**Purpose:** Central configuration for the entire ML pipeline. All other pipeline modules import from here. Contains file paths, the agent→role map, stat field names, and bad-data filter sets.

**Key exports:**

| Constant | Type | Value |
|---|---|---|
| `BASE_DIR` | `str` | Absolute path to the project root |
| `RAW_DB_PATH` | `str` | Path to `match_stats_db.json` |
| `DATA_DIR` | `str` | `ml_pipeline/data/` |
| `MODEL_DIR` | `str` | `ml_pipeline/models/` |
| `PLAYER_STATS_PARQUET` | `str` | Path to `player_stats.parquet` |
| `PLAYER_FEATURES_PARQUET` | `str` | Path to `player_features.parquet` |
| `MATCH_FEATURES_PARQUET` | `str` | Path to `match_features.parquet` |
| `PLAYER_MODEL_PATH` | `str` | Path to `player_performance_rf.pkl` |
| `MATCH_MODEL_PATH` | `str` | Path to `match_win_predictor.pkl` |
| `AGENT_ROLE_MAP` | `dict[str, str]` | Maps every agent name → role (Duelist/Controller/Initiator/Sentinel) |
| `ROLES` | `list[str]` | `["Duelist", "Controller", "Initiator", "Sentinel"]` |
| `STAT_FIELDS` | `list[str]` | Raw stat field names scraped per player |
| `PHASES` | `list[str]` | `["total", "attack", "defense"]` |
| `BAD_AGENTS` | `set[str]` | Agents to ignore during cleaning (incomplete data) |
| `BAD_MAPS` | `set[str]` | Map names to ignore (e.g. `"N/A"`, `"TBD"`) |
| `STAT_COLUMN_MAP` | `dict[str, str]` | Maps raw field keys to readable column name prefixes |

---

#### `data_cleaning.py` (Pipeline Step 1)

**Purpose:** Reads the raw `match_stats_db.json`, parses every player's stat strings (which vlr.gg stores as `"total attack defense"` triplets like `"22 10 12"`) into numeric columns, filters bad data, and saves `player_stats.parquet`.

**Input:** `match_stats_db.json`  
**Output:** `ml_pipeline/data/player_stats.parquet`

**Output schema** (one row per player per map per match):

| Column | Type | Description |
|---|---|---|
| `match_id` | str | vlr.gg match ID |
| `map_id` | str | vlr.gg game (map) ID |
| `map` | str | Map name (e.g. `"Bind"`) |
| `player_name` | str | Player in-game name |
| `agent` | str | Agent played |
| `role` | str | Derived role (Duelist/Controller/etc.) |
| `team` | str | Team name |
| `team_a` | str | First team in match |
| `team_b` | str | Second team in match |
| `winner` | str | Winning team name |
| `is_winner` | int | 1 if this player's team won, 0 otherwise |
| `kills_total` | float | Total kills |
| `kills_attack` | float | Attack-side kills |
| `kills_defense` | float | Defense-side kills |
| `deaths_total` | float | Total deaths |
| `rating_total` | float | Overall rating |
| `acs_total` | float | Average combat score |
| `kast_total` | float | KAST % |
| `adr_total` | float | Average damage per round |
| `hs_pct_total` | float | Headshot % |
| `first_kills_total` | float | First kills |
| `first_deaths_total` | float | First deaths |
| `kd_ratio` | float | Kill/death ratio (derived) |
| `fk_fd_ratio` | float | First-kill/first-death ratio (derived) |
| *(+ attack/defense variants for all stats)* | float | |

**Key functions:**

| Function | Input | Output |
|---|---|---|
| `parse_stat_string(raw)` | Raw string like `"22 10 12"` | `list[float]` of 3 values `[total, attack, defense]` |
| `clean_match_data(db_path)` | Path to JSON DB | `pd.DataFrame` (cleaned) |
| `save_cleaned_data(df, output_path)` | DataFrame, path | Writes parquet |
| `run_cleaning(db_path)` | Path to JSON DB | `pd.DataFrame`; also saves parquet |

**Run:**
```bash
python -m ml_pipeline.run_pipeline --step clean
```

---

#### `feature_engineering.py` (Pipeline Step 2)

**Purpose:** Reads `player_stats.parquet` and builds two higher-level feature tables used for model training:
1. **`player_features.parquet`** — Per-player per-map per-agent aggregated historical stats (averages, win rate, match count).
2. **`match_features.parquet`** — Per-match team-level feature vectors with delta (difference) features and a win label.

**Input:** `ml_pipeline/data/player_stats.parquet`  
**Outputs:** `player_features.parquet`, `match_features.parquet`

**`player_features.parquet` schema** (one row per player × map × agent):

| Column | Description |
|---|---|
| `player_name` | Player name |
| `map` | Map name |
| `agent` | Agent name |
| `role` | Derived role |
| `rating_total` | Mean overall rating across all matches in this group |
| `acs_total` | Mean ACS |
| `kd_ratio` | Mean K/D ratio |
| `kast_total` | Mean KAST % |
| `adr_total` | Mean ADR |
| `hs_pct_total` | Mean headshot % |
| `first_kills_total` | Mean first kills |
| `first_deaths_total` | Mean first deaths |
| `win_rate` | Fraction of matches won (0.0–1.0) |
| `match_count` | Number of matches this group is based on |
| `rating_atk_def_diff` | Attack rating − defense rating |
| `acs_atk_def_diff` | Attack ACS − defense ACS |
| *(+ attack/defense variants for all stats)* | |

**`match_features.parquet` schema** (one row per match played):

| Column | Description |
|---|---|
| `match_id`, `map_id` | Match identifiers |
| `map` | Map name |
| `team_a`, `team_b` | Team names |
| `ta_rating_total_avg` | Team A average rating |
| `ta_acs_total_avg` | Team A average ACS |
| `ta_kd_ratio_avg` | Team A average K/D |
| `ta_num_duelists` | Number of duelists on Team A |
| `ta_rating_attack_avg` | Team A attack-side rating average |
| `ta_rating_defense_avg` | Team A defense-side rating average |
| *(tb_* equivalents for Team B)* | |
| `delta_rating_total_avg` | Team A rating − Team B rating |
| `delta_acs_total_avg` | ACS delta |
| `delta_kd_ratio_avg` | K/D delta |
| `delta_kills_sum` | Total kills delta |
| `delta_fk_sum` | First kills delta |
| `team_a_wins` | **Label**: 1 if Team A won, 0 if Team B won |

**Key functions:**

| Function | Input | Output |
|---|---|---|
| `build_player_features(df)` | Cleaned `pd.DataFrame` | Player features `pd.DataFrame` |
| `build_match_features(df)` | Cleaned `pd.DataFrame` | Match features `pd.DataFrame` |
| `run_feature_engineering(player_stats_path)` | Path to player_stats.parquet | Both DataFrames; also saves parquets |

**Run:**
```bash
python -m ml_pipeline.run_pipeline --step features
```

---

#### `model_training.py` (Pipeline Step 3)

**Purpose:** Trains two scikit-learn pipeline models and saves them as `.pkl` files.

**Model 1 — Player Performance Predictor (`player_performance_rf.pkl`)**
- Algorithm: `RandomForestRegressor` wrapped in `MultiOutputRegressor`
- Input features: map, agent, role (categorical OneHotEncoded) + historical numeric stats
- Targets: `rating_total`, `acs_total` (predicts both simultaneously)
- Preprocessing: OneHotEncoder for categoricals, StandardScaler for numerics

**Model 2 — Match Win Predictor (`match_win_predictor.pkl`)**
- Algorithm: `GradientBoostingClassifier`
- Input features: all `ta_*`, `tb_*`, `delta_*` columns + `map`
- Target: `team_a_wins` (binary 0/1)
- Output: probability via `predict_proba()`

**Key functions:**

| Function | Output |
|---|---|
| `train_player_model(features_path)` | Fitted sklearn `Pipeline`; saves to `player_performance_rf.pkl` |
| `train_match_model(features_path)` | Fitted sklearn `Pipeline`; saves to `match_win_predictor.pkl` |
| `run_training()` | Both models; prints MAE/RMSE/R² (player) and Accuracy/AUC/CV (match) |

**Run:**
```bash
python -m ml_pipeline.run_pipeline --step train
```

---

#### `prediction.py` (Pipeline Step 4 — Advanced Inference)

**Purpose:** Higher-level inference functions that go beyond raw model calls. Provides player predictions, match predictions, team simulation, agent suggestions, and composition optimisation.

**Key functions:**

| Function | Description |
|---|---|
| `predict_player(player_name, map_name, agent)` | Predict rating & ACS for a player; includes historical context and attack/defense breakdown |
| `predict_match(team_a, team_b, map_name)` | Win probability for two 5-player teams on a map; includes strengths analysis |
| `simulate_team(players, opponent, map_name)` | Combines individual + match predictions into a team simulation report |
| `suggest_best_agent(player_name, map_name, top_n=5)` | Ranks all agents a player has history with by predicted rating |
| `suggest_best_composition(player_names, map_name, top_n=5)` | Evaluates agent combinations for 5 players and ranks by predicted team rating + balance score |

*Full input/output contracts are detailed in [Section 6.2](#62-api-contracts-input--output).*

---

#### `run_pipeline.py` — CLI Orchestrator

**Purpose:** Command-line interface for running any pipeline step or inference query. Integrates all four pipeline steps and all prediction functions.

*Full CLI reference in [Section 7](#7-cli-reference).*

---

### 4.3 `analytics_system/` — Analytics & Prediction API

This is the **recommended integration layer** for connecting a frontend or web API. It wraps `ml_pipeline` inference with richer analytics (insights, role balance, player profiles, reasoning).

---

#### `utils.py`

**Purpose:** Shared utilities for the analytics system. Loads models and data files from disk into an in-memory cache (so parquet files and `.pkl` models are only read once per process lifetime), and exposes the agent→role mapping.

**Exports:**

| Export | Type | Description |
|---|---|---|
| `AGENT_ROLE_MAP` | `dict[str, str]` | Agent name → role string |
| `ROLES` | `list[str]` | `["Duelist", "Controller", "Initiator", "Sentinel"]` |
| `load_player_model()` | function | Returns cached sklearn Pipeline (`player_performance_rf.pkl`) |
| `load_match_model()` | function | Returns cached sklearn Pipeline (`match_win_predictor.pkl`) |
| `load_player_features()` | function | Returns cached `pd.DataFrame` from `player_features.parquet` |
| `load_match_features()` | function | Returns cached `pd.DataFrame` from `match_features.parquet` |
| `get_role_for_agent(agent_name)` | function | `str` — role for the given agent, `"Unknown"` if not found |

**Caching:** All four load functions use a module-level `_CACHE` dict. The first call reads from disk; all subsequent calls return the cached object. This makes repeated queries very fast.

---

#### `prediction.py`

**Purpose:** Thin wrappers around the ML models that handle all fallback logic for missing player data (falls back from player+map+agent → player+map → player → global averages).

**Key functions:**

| Function | Input | Output |
|---|---|---|
| `predict_player_performance(player_name, map_name, agent)` | `str, str, str` | `dict` with `predicted_rating`, `predicted_acs`, `historical_avg_rating`, `historical_avg_acs`, `kd_ratio`, `kast`, `adr` |
| `predict_match_outcome(team_a, team_b, map_name)` | Two `list[dict]`, `str` | `dict` with `team_a_win_probability`, `team_b_win_probability` (floats 0–1) |
| `build_team_feature_vector(players, prefix, player_feats)` | Player list, prefix string, features DataFrame | `dict` of prefixed team stat features |

---

#### `analysis.py`

**Purpose:** The main analytics layer. Contains high-level query handlers that produce complete, frontend-ready JSON responses. This is the primary interface a backend web server should call.

**Key functions:**

| Function | Description |
|---|---|
| `process_match_query(team_a, team_b, map_name)` | **Main entry point.** Full match analysis: per-player predictions, team summaries, win probabilities, insights, and reasoning. |
| `process_player_query(player_name)` | Full player profile: career stats, role performance, agent breakdown, strengths/weaknesses. |
| `analyze_team(players, map_name)` | Builds the team data block (called internally by `process_match_query`). |
| `generate_insights(team_a_data, team_b_data)` | Returns list of insight strings about team composition gaps and role fit. |
| `generate_reasoning(team_a_data, team_b_data)` | Returns list of natural-language reasoning strings explaining the prediction. |

*Full input/output contracts in [Section 6.2](#62-api-contracts-input--output).*

---

### 4.4 `legacy_tools/` — Legacy / Utility Scripts

These scripts predate the current `events_scraper` → `ml_pipeline` pipeline. They are not part of the production data path but can still be run independently.

---

#### `scraper.py`

**Purpose:** Extract detailed per-player, per-map stats from a **single vlr.gg match URL**, optionally filtered to one player. Produces rich data including split Attack/Defense stats.

**Key functions:**

| Function | Input | Output |
|---|---|---|
| `extract_map_stats(map_url, target_player_name=None)` | vlr.gg match URL, optional player name | `list[dict]` — one entry per (player × map) or `None` on error |
| `extract_map_names(soup)` | BeautifulSoup object | `list[str]` — ordered map names including `"All"` |
| `extract_map_outcomes(soup, target_player_name)` | BeautifulSoup object, player name | `list[str]` — `"Win"` / `"Loss"` / `"Unknown"` per map |

**Output format per player entry:**
```json
{
  "Player": "TenZ",
  "Map": "Bind",
  "Outcome": "Win",
  "Team": "Sentinels",
  "Agent": "Jett",
  "R": "1.32",
  "ACS": {"All": "287", "Attack": "310", "Defense": "261"},
  "K": "22",
  "D": "14",
  "match_link": "https://www.vlr.gg/..."
}
```

---

#### `scraper_v2.py`

**Purpose:** Leaner scraper that extracts only **agent compositions** (not full stats) from matches. Stores which agents each team played. Reads match URLs from `player_match_links.json`. Writes to `scoutant_v2/match_meta_db.json`.

**DB format:**
```json
"matchId_gameId": {
  "map": "Pearl",
  "winner": "Team Name",
  "team_a": "Team A",
  "team_a_agents": ["Jett", "Omen", "Sova", "Killjoy", "Skye"],
  "team_b": "Team B",
  "team_b_agents": ["Raze", "Viper", "Fade", "Cypher", "Breach"]
}
```

**Run:**
```bash
python legacy_tools/scraper_v2.py          # reads player_match_links.json
python legacy_tools/scraper_v2.py test     # tests against a hardcoded match URL
```

---

#### `team_stats.py`

**Purpose:** Batch scraper. Reads `player_match_links.json`, iterates through all match URLs for every player, calls `scraper.extract_map_stats()`, and accumulates results in `team_player_stats.json`. Saves after every URL, so it is safe to interrupt and resume.

**Input file:** `player_match_links.json` — format: `{"PlayerName": {"links": ["url1", "url2"]}}`  
**Output file:** `team_player_stats.json` — all scraped stats accumulated by player

**Run:**
```bash
python legacy_tools/team_stats.py
```

---

#### `player_links.py`

**Purpose:** Given a list of player names, searches vlr.gg to find each player's numeric ID and slug, then paginates through their match history to collect all match URLs. Saves results to `player_match_links.json`.

**Key functions:**

| Function | Input | Output |
|---|---|---|
| `get_vlr_ids_for_players(player_names)` | `list[str]` | `list[dict]` with `name`, `vlr_id`, `slug` |
| `get_all_match_links(player_id, player_slug)` | int, str | `list[str]` — all match page URLs |
| `scrape_player_matches(player_names)` | `list[str]` (max 5) | Writes `player_match_links.json` |

**Output file format:**
```json
{
  "TenZ": {
    "links": [
      "https://www.vlr.gg/123456/team-a-vs-team-b-...",
      "..."
    ]
  }
}
```

**Run (interactive):**
```bash
python legacy_tools/player_links.py
# Enter up to 5 player names (comma-separated): TenZ, Nats, Zekken
```

---

#### `debug_scraper.py`

**Purpose:** One-off diagnostic script. Fetches a single hardcoded vlr.gg match page and prints the `data-game-id` values and first agent image found in each game div. Used to verify page structure during development.

**Run:**
```bash
python legacy_tools/debug_scraper.py
```

---

#### `event_explorer.py`

**Purpose:** One-off script to explore the structure of vlr.gg's events listing page. Fetches the completed events list, picks the first event, and prints potential match links. Used during development to understand page structure.

**Run:**
```bash
python legacy_tools/event_explorer.py
```

---

### 4.5 Root-Level Files

| File | Purpose |
|---|---|
| `match_stats_db.json` | Raw match database. The source of truth for all ML training data. Format: `{"matches": { "matchId_gameId": { ... } }}` |
| `requirements.txt` | Python package dependencies |
| `test_system.py` | Integration test. Calls `process_match_query` and `process_player_query` with real player names and prints the full JSON response. Run with `python test_system.py` |
| `check_columns.py` | Prints the column names of `match_features.parquet`. Useful for debugging |
| `inspect_data.py` | Data inspection helper script |
| `verify_clean.py` | Verifies the output of the data cleaning step |
| `inspect_output.txt` | Saved output of `inspect_data.py` |
| `inspect_result.txt` | Saved result of data inspection |
| `ml_pipeline_clean_log.txt` | Log from a previous full pipeline run |
| `verify_clean_output.txt` | Saved output of `verify_clean.py` |

---

## 5. Data Flow: End-to-End Pipeline

```
vlr.gg website
     │
     ▼  (events_scraper/Stats_from_events_page.py)
match_stats_db.json                ← Raw JSON: 10 players × map × match
     │
     ▼  (ml_pipeline/data_cleaning.py)
player_stats.parquet               ← 1 row per player per map per match
     │
     ▼  (ml_pipeline/feature_engineering.py)
player_features.parquet            ← 1 row per player × map × agent (aggregated)
match_features.parquet             ← 1 row per match with team vectors + label
     │
     ▼  (ml_pipeline/model_training.py)
player_performance_rf.pkl          ← Predicts rating + ACS
match_win_predictor.pkl            ← Predicts win probability
     │
     ▼  (analytics_system/ or ml_pipeline/prediction.py)
JSON API responses                 ← Consumed by frontend
```

---

## 6. Frontend Integration Guide

### 6.1 Primary Entry Points

For a frontend integration, import from `analytics_system.analysis`:

```python
from analytics_system.analysis import process_match_query, process_player_query
```

For more granular control, import from `ml_pipeline.prediction`:

```python
from ml_pipeline.prediction import (
    predict_player,
    predict_match,
    simulate_team,
    suggest_best_agent,
    suggest_best_composition,
)
```

All functions are **pure Python** — they take plain dicts/strings and return dicts. Wrap them in any web framework (Flask, FastAPI, Django) to expose as HTTP endpoints.

---

### 6.2 API Contracts (Input → Output)

---

#### Match Query: `process_match_query`

```python
from analytics_system.analysis import process_match_query
```

**Input:**
```python
team_a = [
    {"name": "TenZ",   "agent": "Jett"},
    {"name": "Zellsis","agent": "KAY/O"},
    {"name": "johnqt", "agent": "Cypher"},
    {"name": "Sacy",   "agent": "Sova"},
    {"name": "Oxy",    "agent": "Omen"}
]
team_b = [
    {"name": "Demon1", "agent": "Jett"},
    {"name": "Ethan",  "agent": "Skye"},
    {"name": "jawgemo","agent": "Raze"},
    {"name": "Boostio","agent": "Killjoy"},
    {"name": "C0M",    "agent": "Sova"}
]
map_name = "Pearl"

result = process_match_query(team_a, team_b, map_name)
```

**Output schema:**
```json
{
  "map": "Pearl",
  "team_a_win_probability": 0.62,
  "team_b_win_probability": 0.38,
  "confidence": "Medium",
  "model_reasoning": [
    "Team A has higher average rating based on historical performance.",
    "Team A shows stronger combat score (ACS)."
  ],
  "team_a": {
    "players": [
      {
        "name": "TenZ",
        "agent": "Jett",
        "predicted_rating": 1.28,
        "predicted_acs": 265.0,
        "best_role": "Duelist",
        "worst_role": "Sentinel",
        "flexibility_score": 3
      }
    ],
    "summary": {
      "avg_rating": 1.15,
      "avg_acs": 240.5,
      "role_distribution": {
        "duelist": 1,
        "controller": 1,
        "initiator": 2,
        "sentinel": 1
      }
    }
  },
  "team_b": { "...same structure..." },
  "insights": [
    "Team B lacks a controller (smokes).",
    "TenZ is on their most comfortable role (Duelist).",
    "jawgemo is playing their worst role (Duelist). Switch them to Initiator for better performance."
  ],
  "note": "Predictions are probabilistic and not guaranteed outcomes."
}
```

**Confidence levels:** `"High"` (≥ 65%), `"Medium"` (55–65%), `"Low"` (< 55%)

---

#### Player Profile Query: `process_player_query`

```python
from analytics_system.analysis import process_player_query

result = process_player_query("TenZ")
```

**Input:** `player_name: str`

**Output schema:**
```json
{
  "player_name": "TenZ",
  "total_matches": 142,
  "main_role": "Duelist",
  "flexibility_score": 3,
  "average_stats": {
    "rating": 1.24,
    "acs": 271.3,
    "kd_ratio": 1.35,
    "kast": 72.1,
    "adr": 155.8
  },
  "role_performance": {
    "Duelist": 1.28,
    "Initiator": 1.05
  },
  "agent_performance": {
    "Jett": { "rating_total": 1.31, "match_count": 87 },
    "Neon": { "rating_total": 1.18, "match_count": 22 }
  },
  "strengths": [
    "High overall impact (Rating > 1.10).",
    "High combat score.",
    "Consistently positive kill/death ratio."
  ],
  "weaknesses": []
}
```

**Error output** (player not in database):
```json
{ "error": "No data found for PlayerXYZ" }
```

---

#### Player Performance Prediction: `predict_player`

```python
from ml_pipeline.prediction import predict_player

result = predict_player("TenZ", "Bind", "Jett")
```

**Input:** `player_name: str`, `map_name: str`, `agent: str`

**Output schema:**
```json
{
  "player": "TenZ",
  "map": "Bind",
  "agent": "Jett",
  "role": "Duelist",
  "predicted_rating": 1.29,
  "predicted_acs": 278.5,
  "historical": {
    "matches_played": 14,
    "avg_rating": 1.27,
    "avg_acs": 275.0,
    "win_rate": 64.3,
    "avg_kd_ratio": 1.38,
    "rating_attack": 1.35,
    "rating_defense": 1.19,
    "acs_attack": 295.0,
    "acs_defense": 252.0
  },
  "attack_vs_defense": {
    "stronger_side": "attack",
    "rating_differential": 0.16
  }
}
```

---

#### Match Win Prediction: `predict_match`

```python
from ml_pipeline.prediction import predict_match

result = predict_match(team_a, team_b, "Bind")
```

**Input:** `team_a: list[dict]`, `team_b: list[dict]`, `map_name: str`  
Each player dict: `{"name": str, "agent": str}`

**Output schema:**
```json
{
  "map": "Bind",
  "team_a": {
    "players": [{"name": "TenZ", "agent": "Jett"}, "..."],
    "win_probability": 61.5,
    "avg_rating": 1.18,
    "strengths": ["Higher average rating", "Better K/D ratio", "Stronger attack side"]
  },
  "team_b": {
    "players": ["..."],
    "win_probability": 38.5,
    "avg_rating": 1.04,
    "strengths": ["More first kills", "Stronger defense side"]
  },
  "prediction": "Team A",
  "confidence": 61.5
}
```

---

#### Team Simulation: `simulate_team`

```python
from ml_pipeline.prediction import simulate_team

result = simulate_team(my_team, opponent_team, "Lotus")
```

**Input:** `players: list[dict]`, `opponent: list[dict]`, `map_name: str`

**Output schema:**
```json
{
  "map": "Lotus",
  "player_predictions": [
    {
      "player": "TenZ",
      "map": "Lotus",
      "agent": "Jett",
      "predicted_rating": 1.25,
      "predicted_acs": 260.0,
      "historical": { "..." },
      "attack_vs_defense": { "..." }
    }
  ],
  "match_prediction": { "... same as predict_match output ..." },
  "team_summary": {
    "avg_predicted_rating": 1.12,
    "avg_predicted_acs": 242.5
  }
}
```

---

#### Agent Suggestion: `suggest_best_agent`

```python
from ml_pipeline.prediction import suggest_best_agent

result = suggest_best_agent("TenZ", "Bind", top_n=5)
```

**Input:** `player_name: str`, `map_name: str`, `top_n: int = 5`

**Output schema:**
```json
{
  "player": "TenZ",
  "map": "Bind",
  "suggestions": [
    {
      "agent": "Jett",
      "role": "Duelist",
      "predicted_rating": 1.31,
      "predicted_acs": 280.0,
      "matches_played": 14,
      "historical_rating": 1.28
    },
    {
      "agent": "Neon",
      "role": "Duelist",
      "predicted_rating": 1.18,
      "predicted_acs": 255.0,
      "matches_played": 5,
      "historical_rating": 1.15
    }
  ]
}
```

---

#### Composition Suggestion: `suggest_best_composition`

```python
from ml_pipeline.prediction import suggest_best_composition

result = suggest_best_composition(
    ["TenZ", "Zellsis", "johnqt", "Sacy", "Oxy"],
    "Pearl",
    top_n=3
)
```

**Input:** `player_names: list[str]` (exactly 5), `map_name: str`, `top_n: int = 5`

**Output schema:**
```json
{
  "map": "Pearl",
  "player_names": ["TenZ", "Zellsis", "johnqt", "Sacy", "Oxy"],
  "compositions": [
    {
      "players": [
        ["TenZ", "Jett"],
        ["Zellsis", "KAY/O"],
        ["johnqt", "Cypher"],
        ["Sacy", "Sova"],
        ["Oxy", "Omen"]
      ],
      "roles": ["Duelist", "Initiator", "Sentinel", "Initiator", "Controller"],
      "role_dist": {
        "Duelist": 1,
        "Controller": 1,
        "Initiator": 2,
        "Sentinel": 1
      },
      "total_rating": 6.12,
      "score": 6.52
    }
  ]
}
```

**Score** = `total_predicted_rating` + balance bonus (0.1 per role type that has ≥ 1 player).

---

### 6.3 Wrapping in a Web API (Flask / FastAPI example)

**Flask example:**

```python
from flask import Flask, request, jsonify
from analytics_system.analysis import process_match_query, process_player_query
from ml_pipeline.prediction import suggest_best_agent, suggest_best_composition

app = Flask(__name__)

@app.route("/api/match", methods=["POST"])
def match_query():
    data = request.json
    result = process_match_query(data["team_a"], data["team_b"], data["map"])
    return jsonify(result)

@app.route("/api/player/<player_name>", methods=["GET"])
def player_query(player_name):
    result = process_player_query(player_name)
    return jsonify(result)

@app.route("/api/suggest-agent", methods=["GET"])
def agent_suggestion():
    player = request.args.get("player")
    map_name = request.args.get("map")
    result = suggest_best_agent(player, map_name)
    return jsonify(result)

@app.route("/api/suggest-comp", methods=["POST"])
def comp_suggestion():
    data = request.json
    result = suggest_best_composition(data["players"], data["map"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
```

**FastAPI example:**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from analytics_system.analysis import process_match_query, process_player_query

app = FastAPI(title="ScoutAnt API")

class PlayerInput(BaseModel):
    name: str
    agent: str

class MatchRequest(BaseModel):
    team_a: List[PlayerInput]
    team_b: List[PlayerInput]
    map: str

@app.post("/api/match")
def match_endpoint(req: MatchRequest):
    team_a = [p.dict() for p in req.team_a]
    team_b = [p.dict() for p in req.team_b]
    return process_match_query(team_a, team_b, req.map)

@app.get("/api/player/{player_name}")
def player_endpoint(player_name: str):
    return process_player_query(player_name)
```

**Important:** Models and data are cached after the first request (see `analytics_system/utils.py`). Cold-start time is ~1–2 seconds for loading parquet files and `.pkl` models; subsequent requests are fast.

---

## 7. CLI Reference

All pipeline steps and predictions can be run from the command line via `run_pipeline.py`:

```bash
# Full pipeline (clean → features → train)
python -m ml_pipeline.run_pipeline --step all

# Individual pipeline steps
python -m ml_pipeline.run_pipeline --step clean
python -m ml_pipeline.run_pipeline --step features
python -m ml_pipeline.run_pipeline --step train

# Predict player performance
python -m ml_pipeline.run_pipeline --predict-player "TenZ" --map Bind --agent Jett

# Predict match outcome (requires two JSON files)
# team_a.json: [{"name": "TenZ", "agent": "Jett"}, ...]
python -m ml_pipeline.run_pipeline --predict-match team_a.json team_b.json --map Bind

# Simulate a team vs opponent
python -m ml_pipeline.run_pipeline --simulate team_a.json --opponent team_b.json --map Pearl

# Suggest best agent for a player on a map
python -m ml_pipeline.run_pipeline --suggest-agent "TenZ" --map Bind

# Suggest optimal 5-player composition
python -m ml_pipeline.run_pipeline --suggest-comp "TenZ,Zellsis,johnqt,Sacy,Oxy" --map Pearl
```

---

## 8. Data Files Reference

| File | Format | Size | Description |
|---|---|---|---|
| `match_stats_db.json` | JSON | Varies (grows with scraping) | Raw match database. All scraped vlr.gg match data. |
| `ml_pipeline/data/player_stats.parquet` | Parquet | ~MB | Cleaned per-player per-match rows |
| `ml_pipeline/data/player_features.parquet` | Parquet | ~MB | Aggregated player×map×agent feature vectors |
| `ml_pipeline/data/match_features.parquet` | Parquet | ~MB | Team-level match features with win labels |
| `ml_pipeline/models/player_performance_rf.pkl` | Pickle | ~MB | Trained RandomForest player prediction model |
| `ml_pipeline/models/match_win_predictor.pkl` | Pickle | ~MB | Trained GradientBoosting match win model |

---

## 9. Configuration Reference

All configuration lives in `ml_pipeline/config.py`. To change paths or add new agents:

**Adding a new Valorant agent:**
```python
# In ml_pipeline/config.py
AGENT_ROLE_MAP["NewAgent"] = "Duelist"  # or Controller/Initiator/Sentinel
```
Also update the same `AGENT_ROLE_MAP` dict in `analytics_system/utils.py` (it is duplicated there for import independence).

**Changing database path:**
```python
RAW_DB_PATH = os.path.join(BASE_DIR, "my_custom_db.json")
```

**Filtering additional bad agents or maps:**
```python
BAD_AGENTS = {"Unknown", "Miks", "95b78ed7-4637-86d9-7", "AnotherBadEntry"}
BAD_MAPS = {"N/A", "TBD", "Unknown"}
```

After any configuration change that affects the data or features, re-run the full pipeline:
```bash
python -m ml_pipeline.run_pipeline --step all
```
