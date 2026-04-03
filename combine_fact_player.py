from pathlib import Path
import pandas as pd
import re

BASE_DIR = Path(r"C:\Users\Sam\Documents\GitHub\fantasy_football_data_analytics\fact_player_season_output")
OUTPUT_FILE = BASE_DIR / "fact_player_season_master.csv"

all_files = sorted(BASE_DIR.glob("fact_player_season_*.csv"))

dfs = []

for file in all_files:
    match = re.search(r"fact_player_season_(\d{4})\.csv", file.name)
    if not match:
        continue

    year = int(match.group(1))
    df = pd.read_csv(file)

    if "season_year" not in df.columns:
        df["season_year"] = year
    else:
        df["season_year"] = df["season_year"].fillna(year)

    dfs.append(df)

if not dfs:
    raise ValueError("No fact_player_season files found.")

master_df = pd.concat(dfs, ignore_index=True, sort=False)

front_cols = [col for col in ["player", "player_id", "position", "team_name", "franchise_id", "season_year"] if col in master_df.columns]
other_cols = [col for col in master_df.columns if col not in front_cols]
master_df = master_df[front_cols + other_cols]

master_df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved master file: {OUTPUT_FILE}")
print(f"Rows: {len(master_df)}")
print(f"Columns: {len(master_df.columns)}")