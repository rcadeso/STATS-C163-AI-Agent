import sqlite3
import pandas as pd

df_csv = pd.read_csv("summary.csv")

df_csv.columns = df_csv.columns.str.strip()

conn = sqlite3.connect(":memory:")

df_csv.to_sql("tournament_matches", conn, index=False, if_exists="replace")

summary_query = """
WITH normalized_stats AS (
    -- Perspective of Player 1
    SELECT 
        Tournament AS tournament_id, 
        Name_1 AS agent_name, 
        Points_1 AS scored, 
        Points_2 AS conceded,
        CASE WHEN Result_1 = 'W' THEN 1 ELSE 0 END AS win,
        CASE WHEN Result_1 = 'D' THEN 1 ELSE 0 END AS draw,
        CASE WHEN Result_1 = 'L' THEN 1 ELSE 0 END AS loss 
    FROM tournament_matches
    
    UNION ALL
    
    -- Perspective of Player 2
    SELECT 
        Tournament AS tournament_id, 
        Name_2 AS agent_name, 
        Points_2 AS scored, 
        Points_1 AS conceded,
        CASE WHEN Result_2 = 'W' THEN 1 ELSE 0 END AS win,
        CASE WHEN Result_2 = 'D' THEN 1 ELSE 0 END AS draw,
        CASE WHEN Result_2 = 'L' THEN 1 ELSE 0 END AS loss 
    FROM tournament_matches
)
SELECT 
    agent_name AS "Strategy / Agent Name",
    SUM(win) AS "Wins",
    SUM(draw) AS "Draws",
    SUM(loss) AS "Losses",
    SUM(scored) AS "Total Points Scored",
    SUM(scored - conceded) AS "Point Differential"
    
FROM normalized_stats
GROUP BY agent_name
ORDER BY "Wins" DESC, "Losses" DESC;
"""

df_summary = pd.read_sql_query(summary_query, conn)
print("=== TOURNAMENT LEADERBOARD SUMMARY ===")
print(df_summary.to_string(index=False))

filtered_tournament_template = """
WITH normalized_stats AS (
    SELECT 
        Tournament AS tournament_id, Name_1 AS agent_name, Points_1 AS scored, Points_2 AS conceded,
        CASE WHEN Result_1 = 'W' THEN 1 ELSE 0 END AS win,
        CASE WHEN Result_1 = 'D' THEN 1 ELSE 0 END AS draw,
        CASE WHEN Result_1 = 'L' THEN 1 ELSE 0 END AS loss 
    FROM tournament_matches
    WHERE Tournament = :t_id
    
    UNION ALL
    
    SELECT 
        Tournament AS tournament_id, Name_2 AS agent_name, Points_2 AS scored, Points_1 AS conceded,
        CASE WHEN Result_2 = 'W' THEN 1 ELSE 0 END AS win,
        CASE WHEN Result_2 = 'D' THEN 1 ELSE 0 END AS draw,
        CASE WHEN Result_2 = 'L' THEN 1 ELSE 0 END AS loss 
    FROM tournament_matches
    WHERE Tournament = :t_id
)
SELECT 
    agent_name AS "Strategy / Agent Name",
    SUM(win) AS "Wins",
    SUM(draw) AS "Draws",
    SUM(loss) AS "Losses",
    SUM(scored) AS "Total Points Scored",
    SUM(scored - conceded) AS "Point Differential"
FROM normalized_stats
GROUP BY agent_name
ORDER BY "Wins" DESC, "Losses" DESC;
"""

# Fetch the unique tournament IDs present in your CSV dynamically (should be [1, 2, 3])
unique_tournaments = df_csv["Tournament"].unique()

# Loop through and run the filtered query for each tournament
for t_id in sorted(unique_tournaments):
    print(f"=== LEADERBOARD FOR TOURNAMENT {t_id} ===")
    
    # Safely pass the tournament ID parameter into the query execution string
    df_filtered = pd.read_sql_query(filtered_tournament_template, conn, params={"t_id": int(t_id)})
    
    print(df_filtered.to_string(index=False))
    print("-" * 40)


conn.close()
