import requests
from bs4 import BeautifulSoup
import pandas as pd


def parse_liste_col(url):
    url_root = "https://www.cols-cyclisme.com"
    response = requests.get(url)
    webpage = response.content

    # Parse the HTML content
    soup = BeautifulSoup(webpage, 'html.parser')

    # Find the table by its characteristics or location in the webpage
    table = soup.find_all('table')[0]

    # Adjust the headers to include the 'Href' column
    headers = ['href'] # Initialize with 'Href' as the first column
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Extract the rows and hrefs
    data_rows = []
    for row in table.find_all('tr')[1:]:  # skip the header row
        onclick_attr = row.get('onclick', '')
        href = onclick_attr.split("'")[1] if onclick_attr else None
        cols = row.find_all('td')
        data_row = [
            url_root + href] + [col.text.strip() for col in cols]  # Include href as the first item in data_row
        data_rows.append(data_row)

    # Create a DataFrame
    df = pd.DataFrame(data_rows, columns=headers)
    df.reset_index().rename({"index": "id"}, axis = "columns")
    df = df.drop("Détails", axis = "columns")
    return df

# URL of the page to scrape
def extract_info_col(url='https://www.cols-cyclisme.com/arves-et-grandes-rousses/france/auris-en-oisans-depuis-bourg-d-oisans-c2043.htm', id=1):
    response = requests.get(url)
    webpage = response.content
    soup = BeautifulSoup(webpage, 'html.parser')

    details_infos = soup.find('div', id='detail-infos')
    informations = {}
    for tr in details_infos.find_all('tr'):
        key = tr.find_all('td')[0].text.strip()
        value = tr.find_all('td')[1].text.strip()
        informations[key] = value

    # Attempt to find the 'imgprofil' element, handle cases where it does not exist
    profil_img_element = soup.find('p', id='imgprofil')
    if profil_img_element and profil_img_element.find('img'):
        profil_image_url = profil_img_element.find('img')["data-src"]
    else:
        profil_image_url = "Not available"  # Provide a default value or perform alternative actions

    informations['Profil Image URL'] = profil_image_url

    df_col = pd.DataFrame([informations])
    df_col['id'] = id
    df_col.columns = df_col.columns.str.replace(":", "").str.strip()
    return df_col