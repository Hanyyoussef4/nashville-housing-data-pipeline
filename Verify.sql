-- ============================================================
-- Verification queries for the Nashville Housing pipeline.
-- Run after clean_and_load.py to confirm the load completed
-- correctly and the cleaning steps worked as intended.
-- ============================================================

-- Row count should match the original CSV (56477). Confirms every
-- row survived the extract -> clean -> load process with none
-- dropped or duplicated.
select count(*) from nashville_housing;	

-- SaleDate should show as 'timestamp', not 'text' or 'character
-- varying'. Confirms pd.to_datetime() actually converted the column
-- rather than just reformatting the string.
select data_type from information_schema.columns
where table_name = 'nashville_housing' and column_name = 'SaleDate';

-- Spot check that PropertyAddress was correctly split into separate
-- street/city columns, and that SaleDate values look like real dates.
select "SaleDate","PropertyStreet","PropertyCity"
from nashville_housing
limit 10;

-- Should return 0. UniqueID is expected to be unique per row; a
-- non-zero result would mean either the source data has duplicate
-- IDs or something went wrong during the load.
select count(*) - count(distinct "UniqueID") from nashville_housing;

-- Sanity check on column names themselves, not just values -- this
-- caught a real bug: the original "UniqueID" column name had a
-- trailing space from the source CSV header, which pandas carried
-- straight into Postgres. Length should be 8; if it's higher, a
-- column name has hidden whitespace again.
select column_name, length(column_name)
from information_schema.columns
where table_name = 'nashville_housing' and column_name ilike 'uniqueid%';