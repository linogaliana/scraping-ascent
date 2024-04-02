import glob
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import geopandas as gpd
import gpxpy
import time
from pathlib import Path

def parse_liste_col(url, verbose = False):
    url_root = "https://www.cols-cyclisme.com"
    response = requests.get(url)
    webpage = response.content

    soup = BeautifulSoup(webpage, "html.parser")
    table = soup.find_all("table")[0]
    headers = ["href"] + [th.text.strip() for th in table.find_all("th")]
    data_rows = []

    i = 0

    for row in table.find_all("tr")[1:]:  # skip the header row
        onclick_attr = row.get("onclick", "")
        href = onclick_attr.split("'")[1] if onclick_attr else None
        if verbose:
            print(href)
            print(i)
        cols = row.find_all("td")
        data_row = [url_root + href] + [col.text.strip() for col in cols]

        # Fetch the GPX data for the climb
        try:
            climb_page_response = requests.get(url_root + href)
            climb_soup = BeautifulSoup(climb_page_response.content, "html.parser")
            script_tag = climb_soup.find("script", text=re.compile("var gpx"))
            gpx_extract = re.search("var gpx = '(.+?)';", script_tag.string)
            if gpx_extract is None:
                gpx_file_location = None
            else:
                gpx_file_location = gpx_extract.group(1)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GPX data for row {i}: {e}")
            # Store the index of the row with the error for later retry
            # You can add your own error handling logic here
            # For example, you can append the index to a list and try again later
            # retry_list.append(i)
            continue
        
        i += 1

        # Append the GPX data to the row
        data_row.append(gpx_file_location)
        data_rows.append(data_row)
        time.sleep(1)

    # Adjust the headers to include the 'GPX' column
    headers.append("GPX")
    df = pd.DataFrame(data_rows, columns=headers)
    df["GPX"] = url_root + df["GPX"]

    return df


# URL of the page to scrape
def extract_info_col(
    url="https://www.cols-cyclisme.com/arves-et-grandes-rousses/france/auris-en-oisans-depuis-bourg-d-oisans-c2043.htm",
    id=1,
):
    response = requests.get(url)
    webpage = response.content
    soup = BeautifulSoup(webpage, "html.parser")

    details_infos = soup.find("div", id="detail-infos")
    informations = {}
    for tr in details_infos.find_all("tr"):
        key = tr.find_all("td")[0].text.strip()
        value = tr.find_all("td")[1].text.strip()
        informations[key] = value

    # Attempt to find the 'imgprofil' element, handle cases where it does not exist
    profil_img_element = soup.find("p", id="imgprofil")
    if profil_img_element and profil_img_element.find("img"):
        profil_image_url = profil_img_element.find("img")["data-src"]
    else:
        profil_image_url = (
            "Not available"  # Provide a default value or perform alternative actions
        )

    informations["Profil Image URL"] = profil_image_url

    df_col = pd.DataFrame([informations])
    df_col["id"] = id
    df_col.columns = df_col.columns.str.replace(":", "").str.strip()
    return df_col


def create_geojson_from_gpx(three_dim=False):
    files = glob.glob("./gpx/*.gpx")
    geojsons = [gpx_to_geojson(fl, three_dim=three_dim) for fl in files]
    geojsons = pd.concat(geojsons)
    return geojsons


def gpx_to_geojson(filepath, three_dim=False):

    try:
        gpx_file = open(filepath, "r")
        gpx = gpxpy.parse(gpx_file)
        try:
            # Try to access points from tracks
            points = gpx.tracks[0].segments[0].points
        except (IndexError, AttributeError):
            # If there's an error, fallback to routes
            points = gpx.routes[0].points

        longitude = [point.longitude for point in points]
        latitude = [point.latitude for point in points]
        altitude = [point.elevation for point in points]

        z = None
        df = pd.DataFrame({"lon": longitude, "lat": latitude, "alt": altitude})
        if three_dim is True:
            z = df.alt

        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.lon, df.lat, z=z), crs="EPSG:4326"
        )
        gdf["url"] = filepath.rsplit("/", maxsplit=1)[1]
        gdf = gdf.drop(["lon", "lat"], axis="columns")
    except Exception as e:
        return None
    return gdf


def get_gpx_from_url(url):
    if url is not None:
        filename = url.rsplit("/", maxsplit=1)[-1]
        local_path = f"./gpx/{filename}"

        checkgpx = Path(local_path)
        
        if not checkgpx.is_file():
            with open(local_path, "wb") as f:
                f.write(requests.get(url).content)

            try:
                with open(local_path, "r") as gpx_file:
                    gpx = gpxpy.parse(gpx_file)

                    try:
                        # Try to access points from tracks
                        points = gpx.tracks[0].segments[0].points
                    except (IndexError, AttributeError):
                        # If there's an error, fallback to routes
                        points = gpx.routes[0].points

                    longitude = [point.longitude for point in points]
                    latitude = [point.latitude for point in points]
                    altitude = [point.elevation for point in points]

                    df = pd.DataFrame({"lon": longitude, "lat": latitude, "alt": altitude})
                    gdf = gpd.GeoDataFrame(
                        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
                    )
                    gdf["url"] = url
                    gdf = gdf.drop(["lon", "lat"], axis=1)
                    return gdf
            except Exception as e:
                # Handle corrupted GPX or parsing error by returning None
                return None

def get_max_altitude_rows(
    geojsons, group="url", altitude="alt"
):
    df_max_alt = geojsons.sort_values(altitude, ascending=False).drop_duplicates(group)
    return df_max_alt
