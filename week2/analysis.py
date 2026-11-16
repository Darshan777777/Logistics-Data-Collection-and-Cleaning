
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set project paths
project_folder = Path(__file__).resolve().parent.parent
data_file = project_folder / "data" / "processed" / "yellow_tripdata_2024-01_clean.csv"
# Load cleaned dataset
df = pd.read_csv(
    data_file,
    dtype={"store_and_fwd_flag": "string"},
    low_memory=False
)

# Display basic information
print("DATASET LOADED SUCCESSFULLY")
print("-" * 50)

print("\nDataset Shape:")
print(df.shape)

print("\nFirst 5 Records:")
print(df.head())

print("\nColumn Names:")
print(df.columns.tolist())

print("\nDataset Information:")
df.info()

print("\nStatistical Summary:")
print(df.describe(include="all").T)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Records:")
print(df.duplicated().sum())

# ==========================================
# WEEK 2: EXPLORATORY DATA VISUALIZATIONS
# ==========================================

# Create visualization output folder
output_folder = Path(__file__).resolve().parent / "visualizations"
output_folder.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

# Convert relevant columns to numeric/datetime
df["tpep_pickup_datetime"] = pd.to_datetime(
    df["tpep_pickup_datetime"], errors="coerce"
)

df["trip_distance"] = pd.to_numeric(
    df["trip_distance"], errors="coerce"
)

df["trip_duration_minutes"] = pd.to_numeric(
    df["trip_duration_minutes"], errors="coerce"
)

df["total_amount"] = pd.to_numeric(
    df["total_amount"], errors="coerce"
)

# Keep only records within January 2024
original_count = len(df)

df = df[
    (df["tpep_pickup_datetime"] >= "2024-01-01") &
    (df["tpep_pickup_datetime"] < "2024-02-01")
].copy()

excluded_count = original_count - len(df)

# Recreate pickup_date from the validated timestamp
df["pickup_date"] = (
    df["tpep_pickup_datetime"].dt.strftime("%Y-%m-%d")
)

print("\nJANUARY 2024 DATA VALIDATION")
print("Original records:", original_count)
print("Records outside January 2024:", excluded_count)
print("January records used for analysis:", len(df))

# 1. Trip distance distribution
plt.figure(figsize=(10, 5))
sns.histplot(
    data=df,
    x="trip_distance",
    bins=50
)
plt.title("Distribution of Taxi Trip Distances")
plt.xlabel("Trip Distance (miles)")
plt.ylabel("Number of Trips")
plt.xlim(0, 30)
plt.tight_layout()
plt.savefig(output_folder / "01_trip_distance.png", dpi=300)
plt.close()

# 2. Trip duration distribution
plt.figure(figsize=(10, 5))
sns.histplot(
    data=df,
    x="trip_duration_minutes",
    bins=50
)
plt.title("Distribution of Trip Duration")
plt.xlabel("Trip Duration (minutes)")
plt.ylabel("Number of Trips")
plt.xlim(0, 120)
plt.tight_layout()
plt.savefig(output_folder / "02_trip_duration.png", dpi=300)
plt.close()

# 3. Hourly pickup demand
hourly_trips = df.groupby("pickup_hour").size()

plt.figure(figsize=(10, 5))
sns.barplot(
    x=hourly_trips.index,
    y=hourly_trips.values
)
plt.title("Taxi Pickup Demand by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Trips")
plt.tight_layout()
plt.savefig(output_folder / "03_hourly_demand.png", dpi=300)
plt.close()

# 4. Daily pickup demand
daily_trips = (
    df.groupby("pickup_date")
    .size()
    .sort_index()
)

plt.figure(figsize=(12, 5))
plt.plot(daily_trips.index, daily_trips.values, marker="o")
plt.title("Daily Taxi Trip Demand - January 2024")
plt.xlabel("Pickup Date")
plt.ylabel("Number of Trips")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_folder / "04_daily_demand.png", dpi=300)
plt.close()

# 5. Trip distance vs total fare
scatter_data = df[
    ["trip_distance", "total_amount"]
].dropna().sample(
    n=min(20000, len(df)),
    random_state=42
)

plt.figure(figsize=(10, 5))
sns.scatterplot(
    data=scatter_data,
    x="trip_distance",
    y="total_amount",
    alpha=0.3
)
plt.title("Relationship Between Trip Distance and Total Fare")
plt.xlabel("Trip Distance (miles)")
plt.ylabel("Total Amount ($)")
plt.xlim(0, 30)
plt.ylim(-20, 200)
plt.tight_layout()
plt.savefig(output_folder / "05_distance_vs_fare.png", dpi=300)
plt.close()

# 6. Fare distribution by payment type
payment_data = df[
    ["payment_type", "total_amount"]
].dropna()

payment_data = payment_data[
    payment_data["total_amount"].between(0, 200)
]

plt.figure(figsize=(10, 5))
sns.boxplot(
    data=payment_data,
    x="payment_type",
    y="total_amount"
)
plt.title("Fare Distribution by Payment Type")
plt.xlabel("Payment Type Code")
plt.ylabel("Total Amount ($)")
plt.tight_layout()
plt.savefig(output_folder / "06_fare_by_payment.png", dpi=300)
plt.close()

print("\nALL SIX VISUALIZATIONS CREATED SUCCESSFULLY!")
print("Saved in:", output_folder)
print("\nHourly Trip Counts:")
print(hourly_trips)

print("\nDaily Trip Counts:")
print(daily_trips)

# ==========================================
# ADVANCED EDA: LOGISTICS INSIGHTS
# ==========================================

print("\n" + "=" * 55)
print("ADVANCED EXPLORATORY DATA ANALYSIS")
print("=" * 55)

# 1. Weekday vs Weekend Analysis
df["day_type"] = df["tpep_pickup_datetime"].dt.dayofweek.map(
    lambda day: "Weekend" if day >= 5 else "Weekday"
)

day_analysis = df.groupby("day_type").agg(
    total_trips=("day_type", "size"),
    average_distance=("trip_distance", "mean"),
    average_duration=("trip_duration_minutes", "mean"),
    average_fare=("total_amount", "mean")
).round(2)

print("\nWEEKDAY VS WEEKEND ANALYSIS")
print(day_analysis)

day_analysis["total_trips"].plot(
    kind="bar", figsize=(8, 5), rot=0
)
plt.title("Weekday vs Weekend Taxi Demand")
plt.xlabel("Day Type")
plt.ylabel("Number of Trips")
plt.tight_layout()
plt.savefig(output_folder / "07_weekday_vs_weekend.png", dpi=300)
plt.close()


# 2. Payment Method Analysis
payment_analysis = df.groupby("payment_type").agg(
    total_trips=("payment_type", "size"),
    average_fare=("total_amount", "mean"),
    average_tip=("tip_amount", "mean")
).round(2)

print("\nPAYMENT METHOD ANALYSIS")
print(payment_analysis)

payment_analysis["total_trips"].plot(
    kind="bar", figsize=(8, 5), rot=0
)
plt.title("Taxi Trips by Payment Type")
plt.xlabel("Payment Type Code")
plt.ylabel("Number of Trips")
plt.tight_layout()
plt.savefig(output_folder / "08_payment_methods.png", dpi=300)
plt.close()


# 3. Correlation Analysis
numeric_columns = [
    "trip_distance",
    "trip_duration_minutes",
    "fare_amount",
    "tip_amount",
    "total_amount",
    "passenger_count"
]

correlation_matrix = df[numeric_columns].corr()

print("\nCORRELATION MATRIX")
print(correlation_matrix.round(3))

plt.figure(figsize=(10, 7))
sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)
plt.title("Correlation Between Taxi Trip Variables")
plt.tight_layout()
plt.savefig(output_folder / "09_correlation_heatmap.png", dpi=300)
plt.close()


# 4. Top Pickup and Drop-off Locations
top_pickups = df["pulocationid"].value_counts().head(10)
top_dropoffs = df["dolocationid"].value_counts().head(10)

print("\nTOP 10 PICKUP LOCATION IDs")
print(top_pickups)

print("\nTOP 10 DROP-OFF LOCATION IDs")
print(top_dropoffs)

plt.figure(figsize=(10, 6))
sns.barplot(
    x=top_pickups.values,
    y=top_pickups.index
)
plt.title("Top 10 Taxi Pickup Location IDs")
plt.xlabel("Number of Trips")
plt.ylabel("Pickup Location ID")
plt.tight_layout()
plt.savefig(output_folder / "10_top_pickup_locations.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 6))
sns.barplot(
    x=top_dropoffs.values,
    y=top_dropoffs.index
)
plt.title("Top 10 Taxi Drop-off Location IDs")
plt.xlabel("Number of Trips")
plt.ylabel("Drop-off Location ID")
plt.tight_layout()
plt.savefig(output_folder / "11_top_dropoff_locations.png", dpi=300)
plt.close()


# 5. Summary Statistics for Logistics
print("\nLOGISTICS PERFORMANCE SUMMARY")

print("Average trip distance:",
      round(df["trip_distance"].mean(), 2), "miles")

print("Average trip duration:",
      round(df["trip_duration_minutes"].mean(), 2), "minutes")

print("Average total fare:",
      round(df["total_amount"].mean(), 2))

print("Median trip distance:",
      round(df["trip_distance"].median(), 2), "miles")

print("Median trip duration:",
      round(df["trip_duration_minutes"].median(), 2), "minutes")

print("\nALL ADVANCED EDA ANALYSES COMPLETED!")
