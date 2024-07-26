"""Main training pipeline."""

import os

from src import utils
from src.data_cleansing import clean_data
from src.data_gathering import get_data_from_url
from src.data_splitting import split_data
from src.utils import logger


def main():
    """Main Data versioning and ingestion pipeline."""

    config = utils.load_yaml_config()
    logger.info("Data Ingestion Config", extra=config)

    # 1. Gather the data and download it locally
    data_url = os.getenv("DATA_URL", config["data_url"])
    get_data_from_url(data_url, config["data_split"]["raw_data_save_path"])

    # 2. Cleanse the data
    clean_data(config)

    # 3. Load and split the cleansed data
    split_data(config)

    # TODO: check what is the best way to do it from a DAG
    # 4. Update dvc and git - automated way
    # utils.add_to_dvc(config)
    # utils.commit_to_git(config)


if __name__ == "__main__":
    main()
