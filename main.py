import pandas as pd
from scraping import create_geojson_from_gpx, get_max_altitude_rows
from unidecode import unidecode

df = pd.read_parquet("liste.parquet")
df['url'] = df['id']
df['id'] = df['url'].str.rsplit("/").str[-1].str.replace(".gpx", "")


import os

# Create a directory to store the downloaded images
os.makedirs('images', exist_ok=True)

# ----------------
# duplicate images on sspcloud

for url in df['Profil Image URL']:
    # Check if the URL is available
    if url != "Not available":
        # Get the filename from the URL
        filename = url.split('/')[-1]
        
        # Check if the file already exists locally
        if os.path.exists(f'images/{filename}'):
            print(f"Image already exists: {filename}")
        else:
            # Send a GET request to download the image
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Save the image locally
                with open(f'images/{filename}', 'wb') as file:
                    file.write(response.content)
                print(f"Image downloaded: {filename}")
            else:
                print(f"Failed to download image: {filename}")
    else:
        print("Profil Image URL is not available.")
    time.sleep(0.5)


# ----------------
# create geojson for climbind ascent

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


# create geojsons for routes
import os

# Create the 'data/derived/' directory if it doesn't exist
os.makedirs('data/derived/', exist_ok=True)

# Split the routes geodataframe by 'url' column values
split_routes = routes.groupby('url')

split_routes = routes.groupby(['url'])['geometry'].apply(lambda x: LineString(x.tolist()))
split_routes = gpd.GeoDataFrame(split_routes, geometry='geometry')
split_routes = split_routes.groupby("url")

# Write each split into a separate .geojson file
for value, group in split_routes:
    filename = value.replace(".gpx","")
    file_path = f"data/derived/{filename}.geojson"
    group.to_file(file_path, driver='GeoJSON')