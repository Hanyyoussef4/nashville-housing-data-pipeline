
import pandas as pd
housing= pd.read_csv('nashville housing.csv')

# SaleDate arrives as plain text (e.g. "April 9, 2013"). Converting to a
# real datetime type so it can be sorted/filtered correctly in Postgres
# later, instead of being compared as a string.
housing['SaleDate'] = pd.to_datetime(housing['SaleDate'])
print(housing['SaleDate'].dtype)

# PropertyAddress combines street and city into one string (e.g.
# "1808 FOX CHASE DR, GOODLETTSVILLE"). Splitting into separate columns
# so each piece can be queried/filtered independently (e.g. "all sales
# in NASHVILLE") without string-parsing every time.
housing[['PropertyStreet', 'PropertyCity']] = housing ['PropertyAddress'].str.split(',',expand=True)

# The city portion has a leading space from the original comma-split
# format (" GOODLETTSVILLE"). Stripping it so values match exactly for
# grouping/filtering instead of silently splitting into near-duplicates.
housing['PropertyCity'] = housing['PropertyCity'].str.strip()

print(housing[['PropertyStreet', 'PropertyCity']].sample(20).to_string(index=False))

# Original combined address column is redundant now that it's split
# into PropertyStreet/PropertyCity above.
housing = housing.drop(columns=['PropertyAddress'])


# No null-handling for OwnerName, OwnerAddress, and the valuation/building
# columns (Acreage, LandValue, BuildingValue, YearBuilt, Bedrooms, etc.):
# roughly 55% of rows are missing these fields. Dropping rows with any
# null there would remove over half the dataset, and there's no single
# clear cause to justify filling in fake values, so they're left as
# genuine nulls in the database rather than dropped or guessed at.

from sqlalchemy import create_engine
engine = create_engine("postgresql+psycopg2://hany:@localhost:5432/housing_cleaning")

# if_exists="replace" so rerunning this script (e.g. after a code change)
# overwrites the table cleanly instead of appending duplicate rows on
# top of a previous run.
housing.to_sql("nashville_housing", engine, if_exists="replace",index=False)
print("loaded successfully")