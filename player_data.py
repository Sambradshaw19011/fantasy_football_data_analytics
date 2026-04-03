from pathlib import Path
import pandas as pd
from functools import reduce

BASE_DIR = Path(r"C:\Users\Sam\Documents\GitHub\fantasy_football_data_analytics\pff data 2013-2024")
OUTPUT_DIR = BASE_DIR.parent / "fact_player_season_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2013, 2026)

FILE_MAP = {
    "pass": "passing_summary_{year}.csv",
    "rush": "rushing_summary_{year}.csv",
    "rec": "receiving_summary_{year}.csv",
    "def": "defense_summary_{year}.csv",
    "blk": "offense_blocking_{year}.csv",
    "st": "special_teams_summary_{year}.csv",
}

BASE_ID_COLUMNS = [
    "player",
    "player_id",
    "position",
    "team_name",
    "franchise_id"
]

def choose_merge_keys(dfs):
    common = set(dfs[0].columns)
    for df in dfs[1:]:
        common &= set(df.columns)

    preferred = ["player_id", "player", "team_name", "franchise_id", "position"]
    keys = [col for col in preferred if col in common]

    if not keys:
        raise ValueError("No common merge keys found across the input files.")

    return keys

def load_and_prefix(file_path, prefix):
    df = pd.read_csv(file_path)

    id_cols = [col for col in BASE_ID_COLUMNS if col in df.columns]

    rename_cols = {}
    for col in df.columns:
        if col not in id_cols:
            rename_cols[col] = f"{prefix}_{col}"

    df = df.rename(columns=rename_cols)
    return df

def merge_year(year):
    year_folder = BASE_DIR / str(year)
    dfs = []

    if not year_folder.exists():
        print(f"Missing folder for {year}: {year_folder}")
        return None

    for prefix, pattern in FILE_MAP.items():
        file_path = year_folder / pattern.format(year=year)

        if not file_path.exists():
            print(f"Missing file for {year}: {file_path.name}")
            continue

        df = load_and_prefix(file_path, prefix)
        dfs.append(df)

    if not dfs:
        print(f"No files found for {year}")
        return None

    merge_keys = choose_merge_keys(dfs)
    print(f"{year} merge keys: {merge_keys}")

    merged = reduce(
        lambda left, right: pd.merge(left, right, on=merge_keys, how="outer"),
        dfs
    )

    merged["season_year"] = year

    ordered_front = [col for col in ["player", "player_id", "position", "team_name", "franchise_id", "season_year"] if col in merged.columns]
    remaining = [col for col in merged.columns if col not in ordered_front]
    merged = merged[ordered_front + remaining]

    output_file = OUTPUT_DIR / f"fact_player_season_{year}.csv"
    merged.to_csv(output_file, index=False)

    print(f"Saved: {output_file} | Rows: {len(merged)} | Cols: {len(merged.columns)}")
    return merged

for year in YEARS:
    try:
        merge_year(year)
    except Exception as e:
        print(f"Error processing {year}: {e}")