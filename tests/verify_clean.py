"""Quick script to verify the cleaned parquet data."""
import pandas as pd
import os

parquet_path = os.path.join("ml_pipeline", "data", "player_stats.parquet")
if not os.path.exists(parquet_path):
    print(f"ERROR: {parquet_path} not found!")
else:
    df = pd.read_parquet(parquet_path)
    
    lines = []
    lines.append(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    lines.append(f"File size: {os.path.getsize(parquet_path) / (1024*1024):.1f} MB")
    lines.append(f"Unique players: {df['player_name'].nunique()}")
    lines.append(f"Unique maps: {df['map'].nunique()}")
    lines.append(f"Unique agents: {df['agent'].nunique()}")
    lines.append(f"Unique matches: {df['match_id'].nunique()}")
    lines.append(f"\nColumns: {list(df.columns)}")
    lines.append(f"\nMaps: {sorted(df['map'].unique())}")
    lines.append(f"\nAgents: {sorted(df['agent'].unique())}")
    lines.append(f"\nRoles: {df['role'].value_counts().to_dict()}")
    lines.append(f"\nSample row:\n{df.iloc[0].to_string()}")
    lines.append(f"\nNumeric stats summary:")
    lines.append(df[['rating_total','acs_total','kills_total','deaths_total','kd_ratio','adr_total','kast_total']].describe().to_string())
    
    with open("verify_clean_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Wrote verify_clean_output.txt")
