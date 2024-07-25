import pandas as pd
from sklearn.impute import SimpleImputer


def clean_data(config: dict) -> None:
    """Cleanses the data as a preprocessing step."""
    df = pd.read_csv(config["data_split"]["raw_data_save_path"])

    # Define column names
    label_col = config["data_split"]["label_col"]
    categorical_cols = config["data_split"]["categorical_cols"]
    numeric_cols = config["data_split"]["numeric_cols"]

    # 1. Remove duplicates
    df.drop_duplicates(inplace=True)

    # 2. Remove rows where label column has missing values
    df = df.dropna(subset=[label_col])

    # 3. Ensure consistency in data representation
    # by standardize categorical values
    # (e.g., 'Yes' and 'No' instead of 'yes', 'Yes', 'no', 'No')
    for col in categorical_cols:
        df[col] = df[col].str.lower().str.strip()

    # 4. Impute missing values for numerical columns with the median
    numeric_imputer = SimpleImputer(strategy="median")
    df[numeric_cols] = numeric_imputer.fit_transform(df[numeric_cols])

    # 5. Impute missing values for categorical columns
    # with the most frequent value
    categorical_imputer = SimpleImputer(strategy="most_frequent")
    df[categorical_cols] = categorical_imputer.fit_transform(
        df[categorical_cols]
    )

    # 6. Save the cleansed data
    df.to_csv(config["data_split"]["cleansed_data_save_path"])
