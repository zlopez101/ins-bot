from os import stat
from unittest.mock import Mock
import pytest
import requests
import json


class MockResponse:
    def __init__(self, file_path: str, **kwargs):
        self.file_path = file_path
        [setattr(self, name, arg) for name, arg in kwargs.items()]

    def load_json(self) -> dict:
        """Load the mock json data.

        Args:
            file_path (str): path to the specified file

        Returns:
            dict: mock json data
        """
        with open(f"mock_data/{self.file_path}.json", "r") as fp:
            data: dict = json.load(fp)
            return data.get(self.file_path)

    def json(self):
        return self.load_json()


@pytest.fixture
def mock_response(monkeypatch):
    def mock_get(endpoint: str, **kwargs):
        return MockResponse(endpoint, **kwargs)

    monkeypatch.setattr(requests, "get", mock_get)
