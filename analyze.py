import duckdb
import os

# Get the exact folder where this script is located
current_folder = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_folder, "sensor_data.parquet")

print(f"Connecting to DuckDB and reading from: {file_path}\n")

# Connect to an in-memory DuckDB instance
con = duckdb.connect(database=':memory:')

# Create a view that directly queries the Parquet file without loading it all into RAM
con.execute(f"CREATE VIEW sensors AS SELECT * FROM read_parquet('{file_path}')")

# 1. Verify ingestion
count = con.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
print(f"Total records ready for analysis: {count:,}\n")

# 2. Time-Series Aggregation: Calculate hourly average temperature per sensor
print("--- Hourly Average Temperatures (First 6 Rows) ---")
hourly_avg = con.execute("""
    SELECT 
        sensor_id,
        date_trunc('hour', timestamp) AS hour,
        ROUND(AVG(temperature), 2) AS avg_temp,
        ROUND(MAX(temperature), 2) AS max_temp
    FROM sensors
    GROUP BY sensor_id, hour
    ORDER BY hour, sensor_id
    LIMIT 6
""").df()
print(hourly_avg)
print("\n")

# 3. Anomaly Detection: Find extreme temperature spikes (> 40°C)
print("--- Critical Temperature Anomalies (Top 5) ---")
anomalies = con.execute("""
    SELECT * 
    FROM sensors 
    WHERE temperature > 40.0 
    ORDER BY timestamp DESC
    LIMIT 5
""").df()
print(anomalies)