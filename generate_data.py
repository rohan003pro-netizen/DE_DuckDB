import pandas as pd
import numpy as np

print("Generating 1 million sensor readings...")

# Create 1 million timestamps at 1-second intervals
dates = pd.date_range("2026-01-01", periods=1000000, freq="s")

# Simulate 3 different sensors
sensors = np.random.choice(["Sensor_A", "Sensor_B", "Sensor_C"], size=1000000)

# Generate realistic variations (Temp: ~25°C, Humidity: ~50%)
temp = np.random.normal(loc=25.0, scale=5.0, size=1000000)
humidity = np.random.normal(loc=50.0, scale=10.0, size=1000000)

# Compile into a DataFrame and export to Parquet
df = pd.DataFrame({
    "timestamp": dates, 
    "sensor_id": sensors, 
    "temperature": temp, 
    "humidity": humidity
})

df.to_parquet("sensor_data.parquet")
print("Success! Saved as sensor_data.parquet")