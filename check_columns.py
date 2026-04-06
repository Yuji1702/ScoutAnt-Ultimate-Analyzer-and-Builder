import pandas as pd

df = pd.read_parquet("ml_pipeline/data/match_features.parquet")

print(df.columns)