"""Main training pipeline."""

import os

from src import utils
from src.data_cleansing import clean_data
from src.data_gathering import get_data_from_url
from src.data_splitting import split_data
from src.utils import logger


def main():
    """Main Data versioning and ingestion pipeline."""
    config_path = "./config.yaml"

    config = utils.load_yaml_config(config_path)
    logger.info("Data Ingestion Config", extra=config)

    # 1. Gather the data and download it locally
    data_url = os.getenv("DATA_URL", config["data_url"])
    logger.info("Collecting data from source")
    get_data_from_url(data_url, config["data_split"]["raw_data_save_path"])

    # Cleanse the data
    clean_data(config)

    # Load and split the cleansed data
    split_data(config)


if __name__ == "__main__":
    main()
