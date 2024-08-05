"""Unit test for data gathering."""

from unittest.mock import MagicMock, patch

import requests

from src.data_gathering import get_data_from_url


@patch("src.data_gathering.requests.get")
def test_get_data_from_url_success(mock_requests_get):
    """Mock the response object."""
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b"some data"
    mock_requests_get.return_value = mock_response
    mock_response.iter_content = MagicMock(return_value=[b"some data"])

    # Call the function
    url = "http://example.com/data"
    result = get_data_from_url(url)

    # Check if the function returns True
    assert result is True
