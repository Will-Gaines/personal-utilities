import pytest


@pytest.fixture()
def mock_word_list() -> list[str]:
    return ["apple", "bee", "calculator", "do", "engine", "funicular"]
