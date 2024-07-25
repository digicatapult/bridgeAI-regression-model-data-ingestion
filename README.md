# bridgeAI-regression-model-data-ingestion

## Data Ingestion and versioning

1. The data used is available [here](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset).
Provide an accessible path to the csv file in the `config.yaml` file in `data_url`. Please ensure that the file can be downloaded using `curl`. 
Or you can provide the url in the environment variable `DATA_URL`
2. Update the python environment in `.env` file
3. Install `poetry` if not already installed
4. Install the dependencies using poetry `poetry install`
5. update the config and model parameters in the `config.yaml` file
6. Add `./src` to the `PYTHONPATH` - `export PYTHONPATH="${PYTHONPATH}:./src"`
7. Run `poetry run python src/main.py`


### Data ingestion and versioning - using docker
1. Build the docker image - `docker build -t data-ingestion .`
2. Bring up the dependencies by using `docker-compose up -d`
3. Run the container with the correct `DATA_URL` and `DVC_REMOTE` as environment variables.
   (Refer to the following [Environment Variables](#environment-variables) table for complete list)\
   `docker run -e DVC_REMOTE=s3:some/remote -e DATA_URL=https://raw.githubusercontent.com/renjith-digicat/random_file_shares/main/HousingData.csv --rm data-ingestion`


### Environment Variables

The following environment variables can be set to configure the training:

| Variable        | Default Value                                                                                | Description                                                                                                  |
|-----------------|----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| DATA_URL        | `https://raw.githubusercontent.com/renjith-digicat/random_file_shares/main/HousingData.csv ` | Url to the raw data CSV data used for training                                                               |
| CONFIG_PATH     | `./config.yaml`                                                                              | File path to the data cleansing, versioning and other configuration file                                     |
| LOG_LEVEL       | `INFO`                                                                                       | The logging level for the application. Valid values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. |
| DVC_REMOTE      | `/tmp/test-dvc-remote`                                                                       | A DVC remote path                                                                                            |
| DVC_REMOTE_NAME | `regression-model-remote`                                                                    | The name for the dvc remote                                                                                  |


### Running the tests

Ensure that you have the project requirements already set up by following the [Data Ingestion and versioning](#data-ingestion-and-versioning) instructions
- Ensure `pytest` is installed. `poetry install` will install it as a dependency.

[//]: # (- - For integration tests, set up the dependencies &#40;MLFlow&#41; by running, `docker-compose up -d`)
- Run the tests with `poetry run pytest ./tests`