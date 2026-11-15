from pathlib import Path
import requests
import pandas as pd

# 1. Define project folders and source file
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_URL = (
    "https://d37ci6vzurychx.cloudfront.net/trip-data/"
    "yellow_tripdata_2024-01.parquet"
)
RAW_FILE = RAW_DIR / "yellow_tripdata_2024-01.parquet"
CLEAN_FILE = PROCESSED_DIR / "yellow_tripdata_2024-01_clean.csv"

# 2. Download only when the raw file is not already present
if not RAW_FILE.exists():
    response = requests.get(SOURCE_URL, timeout=120)
    response.raise_for_status()
    RAW_FILE.write_bytes(response.content)

# 3. Import and preview
df = pd.read_parquet(RAW_FILE)
print("Shape:", df.shape)
print("\\nColumns:", df.columns.tolist())
print("\\nData types:\\n", df.dtypes)
print("\\nFirst five rows:\\n", df.head())
print("\\nMissing values:\\n", df.isna().sum())

# 4. Keep a copy for before/after reporting
initial_rows = len(df)
initial_columns = len(df.columns)

# 5. Normalize column names
df.columns = (
    df.columns.astype(str)
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
)

# 6. Convert date/time fields to pandas datetime
date_columns = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# 7. Convert expected numeric fields safely
numeric_columns = [
    "passenger_count", "trip_distance", "fare_amount",
    "tip_amount", "total_amount", "PULocationID", "DOLocationID"
]
for col in numeric_columns:
    normalized = col.lower()
    if normalized in df.columns:
        df[normalized] = pd.to_numeric(df[normalized], errors="coerce")

# 8. Remove exact duplicate records
duplicates_removed = int(df.duplicated().sum())
df = df.drop_duplicates()

# 9. Handle missing values
# Do not invent missing timestamps or fares. Rows without essential
# trip timestamps cannot be used for trip-duration analysis.
required = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
existing_required = [c for c in required if c in df.columns]
df = df.dropna(subset=existing_required)

# For optional numeric fields, retain missingness unless a specific
# analysis requires an imputation strategy. Do not replace unknown
# passenger counts or fares with zero automatically.

# 10. Validate trip chronology and plausible ranges
df["trip_duration_minutes"] = (
    df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
).dt.total_seconds() / 60

# Negative/zero duration and negative distance are invalid for this
# basic trip-analysis use case. Extreme values are flagged/filtered
# using transparent thresholds and should be reviewed for the study.
df = df[
    (df["trip_duration_minutes"] > 0) &
    (df["trip_distance"] >= 0)
]

# Example screening limits; these are analytical rules, not TLC rules.
df = df[
    (df["trip_duration_minutes"] <= 24 * 60) &
    (df["trip_distance"] <= 200)
]

# 11. Add useful standardized calendar fields
df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
df["pickup_day_of_week"] = (
    df["tpep_pickup_datetime"].dt.day_name()
)

# 12. Export cleaned dataset
df.to_csv(CLEAN_FILE, index=False)

# 13. Print a concise cleaning summary
print("\\n--- CLEANING SUMMARY ---")
print("Initial rows:", initial_rows)
print("Exact duplicates removed:", duplicates_removed)
print("Final rows:", len(df))
print("Rows removed overall:", initial_rows - len(df))
print("Final columns:", len(df.columns))
print("Cleaned file:", CLEAN_FILE)
print("\\nRemaining missing values:\\n", df.isna().sum())
print("\\nCleaned preview:\\n", df.head())
