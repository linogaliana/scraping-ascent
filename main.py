import pandas as pd
from scraping import create_geojson_from_gpx, get_max_altitude_rows
from unidecode import unidecode

df = pd.read_parquet("liste.parquet")
df['url'] = df['id']
df['id'] = df['url'].str.rsplit("/").str[-1].str.replace(".gpx", "")


geojsons = create_geojson_from_gpx()
df_max_alt = get_max_altitude_rows(geojsons)

df_max_alt["url"] = "https://www.cols-cyclisme.com//gpx/" + df_max_alt["url"]
df_max_alt['id'] = df_max_alt['url'].str.rsplit("/").str[-1].str.replace(".gpx", "")
df_max_alt = df_max_alt.drop("url", axis = "columns")
df_max_alt = df_max_alt.merge(df, on = "id")


sanitized_columns = (df_max_alt.columns
                     .map(unidecode)  # Transliterate characters to ASCII
                     .str.replace('%', 'percent')  # Replace '%' with 'percent'
                     .str.lower()  # Convert to lowercase
                     .str.replace(r'[^a-zA-Z0-9_\s]', '', regex=True)  # Remove special characters except underscores and spaces
                     .str.replace(' ', '_')  # Replace spaces with underscores
                    )
df_max_alt.columns = sanitized_columns
columns_to_sanitize = ['altitude', 'longueur', 'denivellation', 'percent_moyen', 'percent_maximal']
df_max_alt[columns_to_sanitize] = df_max_alt.loc[:,columns_to_sanitize].replace({'\s*': '', 'km': '', 'm': '', '%': ''}, regex=True).astype(float)