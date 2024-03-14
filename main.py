import pandas as pd
from scraping import create_geojson_from_gpx, get_max_altitude_rows

df = pd.read_parquet("liste.parquet")


geojsons = create_geojson_from_gpx()
df_max_alt = get_max_altitude_rows(geojsons)

df_max_alt["url"] = "https://www.cols-cyclisme.com//gpx/" + df_max_alt["url"]
df_max_alt = df_max_alt.merge(df, left_on = "url", right_on = "GPX")
df_max_alt.to_file("alpes-nord-sommet.geojson")