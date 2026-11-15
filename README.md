
# Logistics Data Collection and Cleaning

## Week 1 Internship Assignment

This project demonstrates data collection, inspection, cleaning, and preprocessing using Python and the January 2024 NYC Yellow Taxi Trip Records dataset.

## Dataset

- Source: NYC Taxi & Limousine Commission (TLC)
- Dataset: January 2024 Yellow Taxi Trip Records
- Original shape: 2,964,624 rows × 19 columns

Official dataset:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Technologies Used

- Python 3.12.4
- Pandas
- PyArrow
- Requests
- Visual Studio Code

## Project Structure

```text
Logistics-Data-Collection-and-Cleaning/
├── scripts/
│   └── clean_taxi_data.py
├── data/
│   ├── raw/
│   └── processed/
├── README.md
├── requirements.txt
└── .gitignore
```

## Data Cleaning Results

| Metric | Result |
|---|---:|
| Original rows | 2,964,624 |
| Original columns | 19 |
| Duplicate rows removed | 0 |
| Rows removed overall | 917 |
| Final rows | 2,963,707 |
| Final columns | 23 |

Four additional columns were created:

- trip_duration_minutes
- pickup_date
- pickup_hour
- pickup_day_of_week

Some missing values in optional fields were retained to avoid unnecessary data loss.

## How to Run

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the cleaning script:

```bash
python scripts/clean_taxi_data.py
```

The script downloads the dataset and saves the cleaned CSV in `data/processed/`.

## Learning Outcomes

- Collecting real-world logistics data
- Inspecting datasets using Pandas
- Identifying missing values and duplicates
- Validating trip records
- Creating useful date and time features
- Exporting cleaned data for further analysis

## Internship Assignment

Week 1: Data Collection and Cleaning Strategies in Logistics.
