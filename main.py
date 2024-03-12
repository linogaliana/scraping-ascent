from pathlib import Path
import time
import pandas as pd
import geopandas as gpd

from scraping import (
    parse_liste_col,
    extract_info_col,
    get_gpx_from_url
)


# Fetch the webpage content
url_table_page = 'https://www.cols-cyclisme.com/alpes-du-nord/liste-r1.htm'


# Parse the list of cols and get the DataFrame
#df = parse_liste_col(url_table_page)
#df.to_parquet("liste.parquet")


df = pd.read_parquet("liste.parquet")

# Initialize an empty DataFrame to hold all details
details_df = pd.DataFrame()
traces = gpd.GeoDataFrame()

Path("/gpx").mkdir(parents=True, exist_ok=True)


# Iterate over each row in the DataFrame
for index, row in df.head(10).iterrows():
    col_url = row['href']
    col_info_df = extract_info_col(col_url, id=index)
    col_info_df['url'] = df['GPX']
    trace = get_gpx_from_url(row['GPX'])
    details_df = pd.concat([details_df, col_info_df], ignore_index=True)
    traces = pd.concat([traces, trace])
    time.sleep(1)  # Sleep for 1 second between requests


essai = traces.merge(details_df, on="url")
