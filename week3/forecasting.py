

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned dataset
file_path = "data/processed/yellow_tripdata_2024-01_clean.csv"
df = pd.read_csv(file_path, low_memory=False)

# Convert pickup datetime
df["tpep_pickup_datetime"] = pd.to_datetime(
    df["tpep_pickup_datetime"]
)

# Remove invalid datetime values
df = df.dropna(subset=["tpep_pickup_datetime"])

# Keep January 2024 records
df = df[
    (df["tpep_pickup_datetime"] >= "2024-01-01") &
    (df["tpep_pickup_datetime"] < "2024-02-01")
]

# Create hourly demand
hourly_demand = (
    df.set_index("tpep_pickup_datetime")
      .resample("h")
      .size()
      .reset_index(name="demand")
)

# Create time-based features
hourly_demand["hour"] = (
    hourly_demand["tpep_pickup_datetime"].dt.hour
)

hourly_demand["day_of_week"] = (
    hourly_demand["tpep_pickup_datetime"].dt.day_of_week
)

hourly_demand["is_weekend"] = (
    hourly_demand["day_of_week"] >= 5
).astype(int)

# Create lag features
hourly_demand["lag_1"] = hourly_demand["demand"].shift(1)
hourly_demand["lag_24"] = hourly_demand["demand"].shift(24)
hourly_demand["lag_168"] = hourly_demand["demand"].shift(168)

# Remove missing lag values
hourly_demand = hourly_demand.dropna().reset_index(drop=True)

# Select input features and target
features = [
    "hour",
    "day_of_week",
    "is_weekend",
    "lag_1",
    "lag_24",
    "lag_168"
]

X = hourly_demand[features]
y = hourly_demand["demand"]

# Chronological 80:20 split
split_index = int(len(hourly_demand) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

# Display results
print("Hourly demand data created successfully!")
print("Hourly dataset shape:", (744, 2))

print("\nForecasting features created successfully!")
print("Updated dataset shape:", hourly_demand.shape)

print("\nFeature columns:")
print(hourly_demand.columns.tolist())

print("\nFirst 5 rows:")
print(hourly_demand.head())

print("\nDemand statistics:")
print(hourly_demand["demand"].describe())

print("\nTraining and testing split completed!")
print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print(
    "\nTraining period:",
    hourly_demand["tpep_pickup_datetime"].iloc[0],
    "to",
    hourly_demand["tpep_pickup_datetime"].iloc[split_index - 1]
)

print(
    "Testing period:",
    hourly_demand["tpep_pickup_datetime"].iloc[split_index],
    "to",
    hourly_demand["tpep_pickup_datetime"].iloc[-1]
)

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

# Initialize models
models = {
    "Linear Regression": LinearRegression(),

    "Decision Tree": DecisionTreeRegressor(
        max_depth=10,
        random_state=42
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
}

# Train and predict
predictions = {}
trained_models = {}

for name, model in models.items():

    print(f"\nTraining {name}...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    predictions[name] = y_pred
    trained_models[name] = model

    print(f"{name} training completed!")

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Evaluate model performance
results = []

for name, y_pred in predictions.items():

    mae = mean_absolute_error(y_test, y_pred)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    r2 = r2_score(y_test, y_pred)

    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2 Score": r2
    })

# Create comparison table
results_df = pd.DataFrame(results)

print("\nMODEL PERFORMANCE COMPARISON")
print(results_df.to_string(index=False))

# Identify best model based on MAE
best_model = results_df.loc[results_df["MAE"].idxmin()]

print("\nBEST FORECASTING MODEL")
print("Model:", best_model["Model"])
print("MAE:", round(best_model["MAE"], 2))
print("RMSE:", round(best_model["RMSE"], 2))
print("R2 Score:", round(best_model["R2 Score"], 4))

# Create output folders if they do not exist
import os

os.makedirs("week3/visualizations", exist_ok=True)
os.makedirs("week3/reports", exist_ok=True)

# Get testing timestamps
test_dates = hourly_demand[
    "tpep_pickup_datetime"
].iloc[split_index:]

# Plot actual vs predicted demand
plt.figure(figsize=(14, 6))

plt.plot(
    test_dates,
    y_test.values,
    label="Actual Demand",
    linewidth=2
)

plt.plot(
    test_dates,
    predictions["Random Forest"],
    label="Random Forest Predictions",
    linewidth=2
)

plt.title("Actual vs Predicted Hourly Taxi Demand")
plt.xlabel("Date and Time")
plt.ylabel("Number of Taxi Trips")
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Save graph
plt.savefig(
    "week3/visualizations/random_forest_actual_vs_predicted.png",
    dpi=300
)

plt.show()

print("\nActual vs predicted demand graph saved successfully!")

# Save actual and predicted values for all models
prediction_results = pd.DataFrame({
    "datetime": test_dates.values,
    "actual_demand": y_test.values,
    "linear_regression": predictions["Linear Regression"],
    "decision_tree": predictions["Decision Tree"],
    "random_forest": predictions["Random Forest"]
})

prediction_results.to_csv(
    "week3/reports/test_predictions.csv",
    index=False
)

print("Prediction results saved successfully!")

# Analyze Random Forest feature importance
rf_model = trained_models["Random Forest"]

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": rf_model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\nRANDOM FOREST FEATURE IMPORTANCE")
print(importance_df.to_string(index=False))

# Plot feature importance
plt.figure(figsize=(10, 6))

sns.barplot(
    data=importance_df,
    x="Importance",
    y="Feature"
)

plt.title("Random Forest Feature Importance")
plt.xlabel("Importance Score")
plt.ylabel("Feature")
plt.tight_layout()

# Save visualization
plt.savefig(
    "week3/visualizations/feature_importance.png",
    dpi=300
)

plt.show()

print("\nFeature importance graph saved successfully!")

# Save model performance comparison
results_df.to_csv(
    "week3/reports/model_performance_comparison.csv",
    index=False
)

# Save feature importance results
importance_df.to_csv(
    "week3/reports/feature_importance.csv",
    index=False
)

# Save trained Random Forest model
import joblib

joblib.dump(
    trained_models["Random Forest"],
    "week3/models/random_forest_model.pkl"
)

print("\nFinal analysis files saved successfully!")
print("Model comparison CSV saved.")
print("Feature importance CSV saved.")
print("Random Forest model saved.")
