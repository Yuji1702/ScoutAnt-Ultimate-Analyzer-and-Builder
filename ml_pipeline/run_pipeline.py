"""
run_pipeline.py — CLI orchestrator for the ScoutAnt ML pipeline.

Usage:
    python -m ml_pipeline.run_pipeline --step all
    python -m ml_pipeline.run_pipeline --step clean
    python -m ml_pipeline.run_pipeline --step features
    python -m ml_pipeline.run_pipeline --step train
    python -m ml_pipeline.run_pipeline --predict-player "TenZ" --map Lotus --agent Jett
    python -m ml_pipeline.run_pipeline --predict-match teamA.json teamB.json
    python -m ml_pipeline.run_pipeline --suggest-agent "TenZ" --map Bind
    python -m ml_pipeline.run_pipeline --suggest-comp "player1,player2,player3,player4,player5" --map Pearl
"""

import argparse
import json
import sys
import time

from ml_pipeline.data_cleaning import run_cleaning
from ml_pipeline.feature_engineering import run_feature_engineering
from ml_pipeline.model_training import run_training
from ml_pipeline.prediction import (
    predict_player, predict_match, simulate_team,
    suggest_best_agent, suggest_best_composition,
)


def _print_json(obj):
    """Pretty-print a dict as JSON."""
    print(json.dumps(obj, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        description="ScoutAnt ML Pipeline — Valorant Esports Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline (clean → features → train)
  python -m ml_pipeline.run_pipeline --step all

  # Run individual steps
  python -m ml_pipeline.run_pipeline --step clean
  python -m ml_pipeline.run_pipeline --step features
  python -m ml_pipeline.run_pipeline --step train

  # Predict player performance
  python -m ml_pipeline.run_pipeline --predict-player "TenZ" --map Lotus --agent Jett

  # Suggest best agent for a player
  python -m ml_pipeline.run_pipeline --suggest-agent "TenZ" --map Bind

  # Suggest best team composition
  python -m ml_pipeline.run_pipeline --suggest-comp "player1,player2,player3,player4,player5" --map Pearl
        """,
    )

    # Pipeline steps
    parser.add_argument("--step", choices=["all", "clean", "features", "train"],
                        help="Pipeline step to run")

    # Prediction
    parser.add_argument("--predict-player", metavar="NAME",
                        help="Predict player performance")
    parser.add_argument("--map", help="Map name (e.g. Bind, Lotus, Pearl)")
    parser.add_argument("--agent", help="Agent name (e.g. Jett, Omen)")

    # Match prediction
    parser.add_argument("--predict-match", nargs=2, metavar=("TEAM_A_JSON", "TEAM_B_JSON"),
                        help="Predict match outcome from two JSON files")

    # Simulation
    parser.add_argument("--simulate", metavar="TEAM_JSON",
                        help="Simulate team performance from JSON file")
    parser.add_argument("--opponent", metavar="OPPONENT_JSON",
                        help="Opponent team JSON file (for simulation)")

    # Agent suggestion
    parser.add_argument("--suggest-agent", metavar="NAME",
                        help="Suggest best agent for a player")

    # Composition suggestion
    parser.add_argument("--suggest-comp", metavar="PLAYERS",
                        help="Suggest best composition (comma-separated player names)")

    args = parser.parse_args()

    # ─── Pipeline Steps ──────────────────────────────────────────────────
    if args.step:
        start = time.time()

        if args.step in ("all", "clean"):
            print("\n" + "═" * 60)
            print("STEP 1: DATA CLEANING")
            print("═" * 60)
            run_cleaning()

        if args.step in ("all", "features"):
            print("\n" + "═" * 60)
            print("STEP 2: FEATURE ENGINEERING")
            print("═" * 60)
            run_feature_engineering()

        if args.step in ("all", "train"):
            print("\n" + "═" * 60)
            print("STEP 3: MODEL TRAINING")
            print("═" * 60)
            run_training()

        elapsed = time.time() - start
        print(f"\n⏱️  Pipeline completed in {elapsed:.1f}s")
        return

    # ─── Player Prediction ───────────────────────────────────────────────
    if args.predict_player:
        if not args.map or not args.agent:
            print("❌ --map and --agent are required for player prediction")
            sys.exit(1)
        result = predict_player(args.predict_player, args.map, args.agent)
        _print_json(result)
        return

    # ─── Match Prediction ────────────────────────────────────────────────
    if args.predict_match:
        team_a_file, team_b_file = args.predict_match
        if not args.map:
            print("❌ --map is required for match prediction")
            sys.exit(1)
        with open(team_a_file) as f:
            team_a = json.load(f)
        with open(team_b_file) as f:
            team_b = json.load(f)
        result = predict_match(team_a, team_b, args.map)
        _print_json(result)
        return

    # ─── Simulation ──────────────────────────────────────────────────────
    if args.simulate:
        if not args.opponent or not args.map:
            print("❌ --opponent and --map are required for simulation")
            sys.exit(1)
        with open(args.simulate) as f:
            team = json.load(f)
        with open(args.opponent) as f:
            opponent = json.load(f)
        result = simulate_team(team, opponent, args.map)
        _print_json(result)
        return

    # ─── Agent Suggestion ────────────────────────────────────────────────
    if args.suggest_agent:
        if not args.map:
            print("❌ --map is required for agent suggestion")
            sys.exit(1)
        result = suggest_best_agent(args.suggest_agent, args.map)
        _print_json(result)
        return

    # ─── Composition Suggestion ──────────────────────────────────────────
    if args.suggest_comp:
        if not args.map:
            print("❌ --map is required for composition suggestion")
            sys.exit(1)
        players = [p.strip() for p in args.suggest_comp.split(",")]
        if len(players) != 5:
            print(f"❌ Need exactly 5 players, got {len(players)}")
            sys.exit(1)
        result = suggest_best_composition(players, args.map)
        _print_json(result)
        return

    # No action specified
    parser.print_help()


if __name__ == "__main__":
    main()
