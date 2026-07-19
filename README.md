# Nashville Housing Data Cleaning Pipeline

![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-blue?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-data--cleaning-150458?logo=pandas&logoColor=white)

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
  pandas: strip column-name whitespace,
          parse SaleDate to datetime,
          split PropertyAddress into
          PropertyStreet + PropertyCity
      |
      v
  PostgreSQL (housing_cleaning.nashville_housing)
      |
      v
  verify.sql: row count, dtype, and
              column-name sanity checks
```

## What I found and how I handled it

- **Missing data**: ~55% of rows are missing `OwnerName`, `OwnerAddress`, and valuation fields (`LandValue`, `BuildingValue`, etc.). I initially hypothesized this was because vacant land parcels don't have owner info recorded — checking `LandUse` counts confirmed vacant-land categories only account for about 16% of the missing rows, so most of the missingness has another cause I didn't fully trace. Given the scale (over half the dataset), I left these as nulls rather than dropping rows or filling in guessed values.
- **Duplicate rows**: checked with `.duplicated().sum()` — confirmed zero exact duplicates, so no deduplication was needed. (Note: ~11,000 rows share a `PropertyAddress` with another row, but these are legitimate repeat sales of the same property over the 2013–2016 period, not duplicate records — confirmed by checking that full rows don't match.)
- **Address format**: `PropertyAddress` combined street and city into one string with inconsistent spacing. Split into `PropertyStreet` and `PropertyCity` using `str.split(',', expand=True)`, then stripped stray whitespace from the city field.
- **Hidden whitespace in a column name**: while writing `verify.sql`, a query referencing `"UniqueID"` failed with "column does not exist." Checking `information_schema.columns` showed the actual column name was 9 characters long instead of 8 — the original CSV header had a trailing space that pandas carried straight through into the Postgres table, undetected until it broke a query. Fixed by stripping whitespace from all column names (`housing.columns = housing.columns.str.strip()`), not just column values, right after reading the CSV.

## How to run

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python clean_and_load.py
```

Requires a local PostgreSQL instance with a `housing_cleaning` database already created. After loading, run `verify.sql` (in DBeaver, psql, or any SQL client) to confirm the row count, column types, and column names are correct.

## Dataset

[Housing - SQL Project](https://www.kaggle.com/datasets/bvanntruong/housing-sql-project) by Ann Truong on Kaggle
