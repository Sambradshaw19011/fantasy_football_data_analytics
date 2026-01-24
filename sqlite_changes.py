import sqlite3
from pathlib import Path

DB_PATH = Path("nfl_warehouse.sqlite")

def main():
    print("Opening:", DB_PATH.resolve())

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE fact_player_season
        SET season_id = (
            SELECT season_id
            FROM dim_season
            WHERE dim_season.season_year = fact_player_season.season_year
        )
        WHERE season_id IS NULL;
    """)

    conn.commit()
    print("✅ Update Completed.")

    conn.close()

if __name__ == "__main__":
    main()
