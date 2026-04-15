# Module Documentation: ml_pipeline
The `ml_pipeline` is the data engine of the project. It handles the training and execution of the predictive models.

## Components
- **prediction.py**: The core execution logic for `predict_player` and `predict_match`.
- **counter_logic.py**: Implements the mathematical formula for "Best Counter" (Win Rate $\times$ Map Viability).
- **meta_analysis.py**: Extracts map-wide trends and agent-vs-agent win rates.
- **model_training.py**: Pipeline for training the Random Forest models.
- **config.py**: Defines the `AGENT_ROLE_MAP` and file paths for models and data.

## Data Storage
- **`.parquet` files**: Highly optimized storage for player and match features, enabling fast lookups during real-time predictions.
- **`.pkl` files**: Serialized Scikit-Learn pipelines.
