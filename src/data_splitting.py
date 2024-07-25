"""Data split, preprocess and other data utilities."""

import pandas as pd
from sklearn.model_selection import train_test_split


def split_data(config: dict) -> None:
    """Load a single data source and split it into train, test and val."""
    # read raw data file path from environment variable
    raw_data_path = config["data_split"]["cleansed_data_save_path"]
    data = pd.read_csv(raw_data_path)

    # Split features(X) and target(y) variable
    label_column = config["data_split"]["label_col"]
    X_all = data.drop(label_column, axis=1)
    y_all = data[label_column]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X_all,
        y_all,
        test_size=config["data_split"]["test_frac"],
        random_state=config["data_split"]["seed"],
    )

    # Split the training data further into train and val data
    X_train, X_val, y_train, y_val = train_test_split(
        X_train,
        y_train,
        test_size=config["data_split"]["val_frac"],
        random_state=config["data_split"]["seed"],
    )

    # Combine features and labels into a dataframe
    X_train[config["data_split"]["label_col"]] = y_train
    X_test[config["data_split"]["label_col"]] = y_test
    X_val[config["data_split"]["label_col"]] = y_val

    # Save the split dataframes into csvs
    X_train.to_csv(config["data_split"]["train_data_save_path"], index=False)
    X_val.to_csv(config["data_split"]["val_data_save_path"], index=False)
    X_test.to_csv(config["data_split"]["test_data_save_path"], index=False)
