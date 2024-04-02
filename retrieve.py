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
# url_table_page = 'https://www.cols-cyclisme.com/alpes-du-nord/liste-r1.htm'
# url_table_page = 'https://www.cols-cyclisme.com/alpes-du-sud/liste-r2.htm'
url_table_page = 'https://www.cols-cyclisme.com/pyrenees/liste-r3.htm'

def retrieve_save_details(url_table_page):
    filename = (
        url_table_page
        .rsplit("/", maxsplit=1)[1]
        .split(".")[0]
    )
    filename = f"{filename}.parquet"

    # Parse the list of cols and get the DataFrame
    df = parse_liste_col(url_table_page)

    details = [extract_info_col(df['href'][i], df['GPX'][i]) for i in range(len(df))]
    details_augmented = pd.concat(details)
    details_augmented = details_augmented.merge(
        df.loc[:, ['GPX', 'href']],
        left_on="id", right_on="GPX").drop("GPX", axis="columns")
    details_augmented.to_parquet(filename)
    return details_augmented

details_augmented = retrieve_save_details(url_table_page)

# Initialize an empty DataFrame to hold all details
details_df = pd.DataFrame()
traces = gpd.GeoDataFrame()

Path("./gpx").mkdir(parents=True, exist_ok=True)

#details_df_old = pd.DataFrame()
#traces_old = gpd.GeoDataFrame()
details_df_old = pd.DataFrame()
details_df = pd.DataFrame()
traces = gpd.GeoDataFrame()

# Iterate over each row in the DataFrame
for index, row in details_augmented.iterrows():
    if pd.notnull(row['id']) # and row['id'] not in details_df_old['url'].tolist():
        print(f"{index}, {row['id']}")
        col_url = row['href']
        col_info_df = extract_info_col(col_url, id=index)
        col_info_df['url'] = row['id']
        trace = get_gpx_from_url(row['id'])
        details_df = pd.concat([details_df, col_info_df], ignore_index=True)
        traces = pd.concat([traces, trace])
        time.sleep(1)  # Sleep for 1 second between requests