# Nashville Housing Data Cleaning Pipeline

A small end-to-end data pipeline: extract messy housing sales data from a CSV, clean it with pandas, and load it into PostgreSQL for querying.

## Problem

The raw dataset (Nashville property sales, 2013–2016) has three real data quality issues: sale dates stored as inconsistent text, a combined address field mixing street and city into one string, and heavy missing data in ownership/valuation fields.

## Tech stack

Python, pandas, SQLAlchemy, psycopg2, PostgreSQL

## Pipeline

```
CSV (Nashville Housing.csv)
      |
      v
  pandas: parse SaleDate to datetime,
          split PropertyAddress into
          PropertyStreet + PropertyCity
      |
      v
  PostgreSQL (housing_cleaning.nashville_housing)
```

## What I found and how I handled it

- **Missing data**: ~55% of rows are missing `OwnerName`, `OwnerAddress`, and valuation fields (`LandValue`, `BuildingValue`, etc.). I initially hypothesized this was because vacant land parcels don't have owner info recorded — checking `LandUse` counts confirmed vacant-land categories only account for about 16% of the missing rows, so most of the missingness has another cause I didn't fully trace. Given the scale (over half the dataset), I left these as nulls rather than dropping rows or filling in guessed values.
- **Duplicate rows**: checked with `.duplicated().sum()` — confirmed zero exact duplicates, so no deduplication was needed. (Note: ~11,000 rows share a `PropertyAddress` with another row, but these are legitimate repeat sales of the same property over the 2013–2016 period, not duplicate records — confirmed by checking that full rows don't match.)
- **Address format**: `PropertyAddress` combined street and city into one string with inconsistent spacing. Split into `PropertyStreet` and `PropertyCity` using `str.split(',', expand=True)`, then stripped stray whitespace from the city field.

## How to run

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python clean_and_load.py
```

Requires a local PostgreSQL instance with a `housing_cleaning` database already created.

## Dataset

[Housing - SQL Project](https://www.kaggle.com/datasets/bvanntruong/housing-sql-project) by Ann Truong on Kaggle
