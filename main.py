import time
import pandas as pd

from scraping import (
    parse_liste_col,
    extract_info_col
)

# Fetch the webpage content
url_table_page = 'https://www.cols-cyclisme.com/alpes-du-nord/liste-r1.htm'


# Parse the list of cols and get the DataFrame
df = parse_liste_col(url_table_page)

# Initialize an empty DataFrame to hold all details
details_df = pd.DataFrame()

# Iterate over each row in the DataFrame
for index, row in df.head(10).iterrows():
    col_url = row['href']
    col_info_df = extract_info_col(col_url, id=index)
    details_df = pd.concat([details_df, col_info_df], ignore_index=True)
    time.sleep(1)  # Sleep for 1 second between requests
