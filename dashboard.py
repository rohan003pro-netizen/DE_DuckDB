import streamlit as st
import duckdb
import os
import altair as alt

st.set_page_config(page_title="IoT Sensor Dashboard", layout="wide")
st.title("🌡️ IoT Sensor Analytics Pipeline")

current_folder = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_folder, "sensor_data.parquet")

@st.cache_data
def fetch_analytics():
    con = duckdb.connect(database=':memory:')
    con.execute(f"CREATE VIEW sensors AS SELECT * FROM read_parquet('{file_path}')")
    
    total_records = con.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
    max_temp = con.execute("SELECT ROUND(MAX(temperature), 2) FROM sensors").fetchone()[0]
    anomaly_count = con.execute("SELECT COUNT(*) FROM sensors WHERE temperature > 40.0").fetchone()[0]

    # Return actual datetimes for the hour (not strings) so Altair can space the axis smartly
    hourly = con.execute("""
        SELECT 
            date_trunc('hour', timestamp) AS hour,
            sensor_id,
            ROUND(AVG(temperature), 2) AS avg_temp
        FROM sensors
        GROUP BY hour, sensor_id
        ORDER BY hour
    """).df()
    
    anomalies = con.execute("""
        SELECT 
            strftime(timestamp, '%Y-%m-%d %H:%M:%S') AS timestamp,
            sensor_id, 
            ROUND(temperature, 2) AS temp_c, 
            ROUND(humidity, 2) AS hum_pct 
        FROM sensors 
        WHERE temperature > 40.0 
        ORDER BY timestamp DESC
    """).df()
    
    return total_records, max_temp, anomaly_count, hourly, anomalies

total_records, max_temp, anomaly_count, hourly_data, anomaly_data = fetch_analytics()

# KPI Metric Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Ingested Records", f"{total_records:,}")
col2.metric("Peak Temperature Recorded", f"{max_temp} °C")
col3.metric("Critical Anomalies Detected", f"{anomaly_count:,}")

st.write("---")

# Altair Chart Setup
st.subheader("Hourly Average Temperature Trends")

chart = alt.Chart(hourly_data).mark_line().encode(
    x=alt.X('hour:T', title='Time'),
    # scale=alt.Scale(zero=False) prevents the chart from flattening by zooming in on the data range
    y=alt.Y('avg_temp:Q', scale=alt.Scale(zero=False), title='Avg Temperature (°C)'),
    color=alt.Color('sensor_id:N', title='Sensor'),
    tooltip=['hour:T', 'sensor_id:N', 'avg_temp:Q']
).properties(height=400).interactive()

st.altair_chart(chart, use_container_width=True)

st.subheader("⚠️ Critical Anomalies (> 40°C)")
st.dataframe(anomaly_data, use_container_width=True, height=260)