"""
model_training.py — Step 3: Train ML models for prediction.

Model 1: Player Performance Predictor (RandomForestRegressor)
  - Predicts rating_total and acs_total given map, agent, role, historical stats

Model 2: Match Win Predictor (GradientBoostingClassifier)
  - Predicts probability of team_a winning given team features
"""

import os
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, roc_auc_score, classification_report,
)

from ml_pipeline.config import (
    PLAYER_FEATURES_PARQUET, MATCH_FEATURES_PARQUET,
    PLAYER_MODEL_PATH, MATCH_MODEL_PATH, MODEL_DIR,
)


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL 1: PLAYER PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

def train_player_model(features_path: str = PLAYER_FEATURES_PARQUET):
    """
    Train a RandomForest model to predict player rating and ACS.
    
    Input features: map, agent, role, historical averages, match_count
    Targets: rating_total, acs_total
    """
    print("=" * 60)
    print("🤖 Training Player Performance Model")
    print("=" * 60)

    df = pd.read_parquet(features_path)
    print(f"   Loaded {df.shape[0]} player feature rows")

    # Filter: need minimum sample size
    min_matches = 3
    df = df[df["match_count"] >= min_matches].copy()
    print(f"   After filtering (>={min_matches} matches): {df.shape[0]} rows")

    if df.shape[0] < 100:
        print("   ⚠️  Not enough data to train. Skipping player model.")
        return None

    # ─── Feature & Target Selection ──────────────────────────────────────
    categorical_features = ["map", "agent", "role"]

    numeric_features = [
        "kills_total", "deaths_total", "assists_total",
        "kd_ratio", "kd_ratio_attack", "kd_ratio_defense",
        "fk_fd_ratio",
        "kast_total", "adr_total", "hs_pct_total",
        "first_kills_total", "first_deaths_total",
        "match_count", "win_rate",
        "kills_attack", "kills_defense",
        "deaths_attack", "deaths_defense",
        "rating_attack", "rating_defense",
        "acs_attack", "acs_defense",
    ]

    # Only keep columns that actually exist
    numeric_features = [c for c in numeric_features if c in df.columns]

    targets = ["rating_total", "acs_total"]

    # Drop rows with NaN in targets
    df = df.dropna(subset=targets)

    X = df[categorical_features + numeric_features]
    y = df[targets]

    # ─── Preprocessing Pipeline ──────────────────────────────────────────
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", StandardScaler(), numeric_features),
        ],
        remainder="drop",
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", MultiOutputRegressor(
            RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )
        )),
    ])

    # ─── Train / Test Split ──────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"   Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
    print("   Training...")

    model.fit(X_train, y_train)

    # ─── Evaluation ──────────────────────────────────────────────────────
    y_pred = model.predict(X_test)

    for i, target in enumerate(targets):
        mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
        rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], y_pred[:, i]))
        r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
        print(f"\n   📈 {target}:")
        print(f"      MAE:  {mae:.4f}")
        print(f"      RMSE: {rmse:.4f}")
        print(f"      R²:   {r2:.4f}")

    # ─── Cross Validation ────────────────────────────────────────────────
    # print("\n   Running 5-fold cross-validation (on rating)...")
    # cv_scores = cross_val_score(
    #     model, X, y, cv=5, scoring="r2", n_jobs=-1
    # )
    # print(f"   CV R² scores: {[f'{s:.4f}' for s in cv_scores]}")
    # print(f"   CV R² mean:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ─── Save ────────────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, PLAYER_MODEL_PATH)
    print(f"\n   💾 Saved player model to {PLAYER_MODEL_PATH}")

    return model


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL 2: MATCH WIN PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

def train_match_model(features_path: str = MATCH_FEATURES_PARQUET):
    """
    Train a GradientBoosting classifier to predict match winner.
    
    Input: team_a features, team_b features, delta features
    Target: team_a_wins (binary)
    """
    print("\n" + "=" * 60)
    print("🤖 Training Match Win Prediction Model")
    print("=" * 60)

    df = pd.read_parquet(features_path)
    print(f"   Loaded {df.shape[0]} match feature rows")

    if df.shape[0] < 100:
        print("   ⚠️  Not enough data to train. Skipping match model.")
        return None

    # ─── Feature Selection ───────────────────────────────────────────────
    # Use all ta_*, tb_*, delta_* columns as features
    feature_cols = [
        c for c in df.columns
        if c.startswith(("ta_", "tb_"))
        and not any(x in c for x in [
            "kills", "deaths", "kd", "fk", "fd"
        ])
    ]

    # Map as categorical
    categorical_features = ["map"]
    numeric_features = feature_cols

    target = "team_a_wins"

    df = df.dropna(subset=[target])

    # Fill NaN in features with 0
    df[numeric_features] = df[numeric_features].fillna(0)

    X = df[categorical_features + numeric_features]
    y = df[target]

    # ─── Preprocessing Pipeline ──────────────────────────────────────────
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", StandardScaler(), numeric_features),
        ],
        remainder="drop",
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", GradientBoostingClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=42,
        )),
    ])

    # ─── Train / Test Split ──────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"   Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
    print(f"   Label distribution: {y.value_counts().to_dict()}")
    print("   Training...")

    model.fit(X_train, y_train)

    # ─── Evaluation ──────────────────────────────────────────────────────
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print(f"\n   📈 Match Win Prediction:")
    print(f"      Accuracy: {accuracy:.4f}")
    print(f"      AUC-ROC:  {auc:.4f}")
    print(f"\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Team B wins", "Team A wins"]))

    # ─── Cross Validation ────────────────────────────────────────────────
    print("   Running 5-fold cross-validation...")
    cv_scores = cross_val_score(
        model, X, y, cv=5, scoring="roc_auc", n_jobs=-1
    )
    print(f"   CV AUC scores: {[f'{s:.4f}' for s in cv_scores]}")
    print(f"   CV AUC mean:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ─── Feature Importance ──────────────────────────────────────────────
    # Get feature names after preprocessing
    try:
        cat_names = model.named_steps["preprocessor"].transformers_[0][1].get_feature_names_out(categorical_features)
        all_feature_names = list(cat_names) + numeric_features
        importances = model.named_steps["classifier"].feature_importances_
        importance_df = pd.DataFrame({
            "feature": all_feature_names,
            "importance": importances
        }).sort_values("importance", ascending=False).head(15)
        print(f"\n   🔑 Top 15 Feature Importances:")
        for _, row in importance_df.iterrows():
            print(f"      {row['feature']:40s} {row['importance']:.4f}")
    except Exception:
        pass

    # ─── Save ────────────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MATCH_MODEL_PATH)
    print(f"\n   💾 Saved match model to {MATCH_MODEL_PATH}")

    return model


# ═══════════════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════════════

def run_training():
    """Train both models."""
    player_model = train_player_model()
    match_model = train_match_model()
    print("\n✅ All models trained and saved.")
    return player_model, match_model


if __name__ == "__main__":
    run_training()
