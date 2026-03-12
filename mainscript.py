import pandas as pd
import geopandas
import matplotlib
import openpyxl

# df = pd.read_excel("Dataset/ModernSamples/GeneticDistances.xlsx")
# df

import polars as pl

aadr = pl.read_excel("Dataset/AADR.xlsx")
aadr = aadr.rename({"Date mean in BP in years before 1950 CE [OxCal mu for a direct radiocarbon date, and average of range for a contextual date]": "Date"})
# aadr.schema
fil = aadr.filter((pl.col("Date") > 700) & (pl.col("Date") < 1100) & (pl.col("Group ID").str.contains("Iceland"))).select("Master ID", "Date", "Group ID")
with pl.Config(tbl_rows=50):
    print(fil)

gendist = pl.read_excel("Dataset/GeneticDistance_aDNA.xlsx")
target_ID = fil.select("Master ID").unique()
gendist_prep = gendist.with_columns([pl.col("col1").is_in(df3_ids["col1"]).alias("col1_matched"), pl.col("col2").is_in(df3_ids["col1"]).alias("col2_matched")])