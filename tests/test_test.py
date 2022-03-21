import pytest
import requests
from .conftest import MockResponse


def test_mock_get(mock_response):
    response = requests.get("codes", status_code=200)
    assert isinstance(response, MockResponse)
    assert response.status_code == 200
