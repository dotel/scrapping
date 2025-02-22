import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
url = "https://raw.githubusercontent.com/dotel/scrapping/main/chargers_data.csv"
df = pd.read_csv(url)

# Convert timestamp to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Compute utilization percentage
df['Utilization (%)'] = (1 - df['Available Chargers'] / df['Total Chargers']) * 100

# Aggregate utilization per station
station_utilization = df.groupby('Station')['Utilization (%)'].mean().reset_index()

# Plot average utilization per station
plt.figure(figsize=(10, 5))
sns.barplot(x="Utilization (%)", y="Station", data=station_utilization, palette="viridis")
plt.xlabel("Average Utilization (%)")
plt.ylabel("Charging Station")
plt.title("Average Charging Station Utilization")
plt.show()

# Utilization over time
plt.figure(figsize=(12, 6))
sns.lineplot(x="Timestamp", y="Utilization (%)", hue="Station", data=df, marker="o")
plt.xticks(rotation=45)
plt.xlabel("Time")
plt.ylabel("Utilization (%)")
plt.title("Charging Station Utilization Over Time")
plt.legend(loc='upper right')
plt.show()
