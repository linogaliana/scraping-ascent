import os
import requests
import time

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
from unidecode import unidecode

from scraping import create_geojson_from_gpx, get_max_altitude_rows

# Create a directory to store the downloaded images
os.makedirs("images", exist_ok=True)
os.makedirs("data/derived/", exist_ok=True)


df = pd.read_parquet("liste-r2.parquet")

df["url"] = df["id"]
df["id"] = df["url"].str.rsplit("/").str[-1].str.replace(".gpx", "")


# ----------------------------------
# duplicate images on sspcloud

for url in df["Profil Image URL"]:
    # Check if the URL is available
    if url != "Not available":
        # Get the filename from the URL
        filename = url.split("/")[-1]

        # Check if the file already exists locally
        if os.path.exists(f"images/{filename}"):
            print(f"Image already exists: {filename}")
        else:
            time.sleep(1)
            # Send a GET request to download the image
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Save the image locally
                with open(f"images/{filename}", "wb") as file:
                    file.write(response.content)
                print(f"Image downloaded: {filename}")
            else:
                print(f"Failed to download image: {filename}")
    else:
        print("Profil Image URL is not available.")


# ---------------------------------------
# create geojson for climbing ascent

filename_summits = "alpes-sud-sommets.geojson"

geojsons = create_geojson_from_gpx()
df_max_alt = get_max_altitude_rows(geojsons)

df_max_alt["url"] = "https://www.cols-cyclisme.com//gpx/" + df_max_alt["url"]
df_max_alt["id"] = df_max_alt["url"].str.rsplit("/").str[-1].str.replace(".gpx", "")
df_max_alt = df_max_alt.drop("url", axis="columns")
df_max_alt = df_max_alt.merge(df, on="id")


sanitized_columns = (
    df_max_alt.columns.map(unidecode)  # Transliterate characters to ASCII
    .str.replace("%", "percent")  # Replace '%' with 'percent'
    .str.lower()  # Convert to lowercase
    .str.replace(
        r"[^a-zA-Z0-9_\s]", "", regex=True
    )  # Remove special characters except underscores and spaces
    .str.replace(" ", "_")  # Replace spaces with underscores
)
df_max_alt.columns = sanitized_columns
columns_to_sanitize = [
    "altitude",
    "longueur",
    "denivellation",
    "percent_moyen",
    "percent_maximal",
]
df_max_alt[columns_to_sanitize] = (
    df_max_alt.loc[:, columns_to_sanitize]
    .replace({r"\s*": "", "km": "", "m": "", "%": ""}, regex=True)
    .astype(float)
)
df_max_alt['vtt'] = (
    df_max_alt['vtt'] == "ATTENTION : cette ascension nécéssite l'utilisation d'un VTT"
)
df_max_alt = df_max_alt.drop("ouverture", axis="columns")
df_max_alt["category"] = pd.cut(
    df_max_alt["denivellation"],
    right=False,
    bins=[80, 160, 320, 640, 800, float("inf")], 
    labels=["Cat 4", "Cat 3", "Cat 2", "Cat 1", "HC"]
)
df_max_alt["category"] = df_max_alt["category"].astype(str)
df_max_alt.to_file(filename_summits)


# Create routes ----------------------------------

routes = create_geojson_from_gpx(three_dim=True)

# Split the routes geodataframe by 'url' column values
split_routes = routes.groupby("url")

split_routes = routes.groupby(["url"])["geometry"].apply(
    lambda x: LineString(x.tolist())
)
split_routes = gpd.GeoDataFrame(split_routes, geometry="geometry")
split_routes = split_routes.groupby("url")

# Write each split into a separate .geojson file
for value, group in split_routes:
    filename = value.replace(".gpx", "")
    file_path = f"data/derived/{filename}.geojson"
    group.to_file(file_path, driver="GeoJSON")

