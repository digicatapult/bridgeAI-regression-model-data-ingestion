"""Collect available data from source(s).


This module should:
    - collect data from different source like database, datalake or other
    - combine them into a single dataset
    - save the data locally for the rest of the data ingestion and
        versioning pipeline can work
"""

import requests

from utils import logger


def get_data_from_url(url: str, output_path: str = "data.csv") -> bool:
    """
    Get data from a URL and save it to a local file.

    Args:
        url (str): The URL to download data from
        output_path (str): The local path to save the downloaded file

    Returns:
        bool: True if the download was successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                file.write(chunk)
        logger.info(f"Data downloaded successfully from - {url}")
        return True
    except requests.RequestException as e:
        logger.error(f"Error downloading data from - {url}: \n{e}")
        raise e
