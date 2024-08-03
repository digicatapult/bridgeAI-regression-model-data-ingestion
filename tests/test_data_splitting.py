"""Unit test for data splitting."""

from unittest.mock import patch

import pandas as pd
import pytest

from src.data_splitting import split_data

# Test config
config = {
    "data_split": {
        "cleansed_data_save_path": "fake_path.csv",
        "label_col": "target",
        "test_frac": 0.2,
        "val_frac": 0.25,
        "seed": 42,
        "train_data_save_path": "train_data.csv",
        "val_data_save_path": "val_data.csv",
        "test_data_save_path": "test_data.csv",
    }
}


@pytest.fixture
def mock_data():
    """Mock data."""
    return pd.DataFrame(
        {
            "feature1": [1, 2, 3, 4, 5],
            "feature2": [10, 20, 30, 40, 50],
            "target": [0, 1, 0, 1, 0],
        }
    )


@patch("src.data_splitting.pd.read_csv")
@patch("src.data_splitting.pd.DataFrame.to_csv")
@patch("src.data_splitting.train_test_split")
def test_split_data(
    mock_train_test_split, mock_to_csv, mock_read_csv, mock_data
):
    """Test successful data splitting."""
    # Mock the read_csv method
    mock_read_csv.return_value = mock_data

    # Mock train_test_split method
    mock_train_test_split.side_effect = [
        (
            mock_data[["feature1", "feature2"]],
            mock_data[["feature1", "feature2"]],
            mock_data["target"],
            mock_data["target"],
        ),  # First split
        (
            mock_data[["feature1", "feature2"]],
            mock_data[["feature1", "feature2"]],
            mock_data["target"],
            mock_data["target"],
        ),  # Second split
    ]

    # Mock to_csv method
    mock_to_csv.return_value = None

    split_data(config)

    # Check if to_csv was called with the correct file path
    mock_to_csv.assert_called_with(
        config["data_split"]["test_data_save_path"], index=False
    )
