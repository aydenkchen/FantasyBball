import os


def test_oauth_example_exists():
    assert os.path.exists(
        "oauth2.example.json"
    ), "oauth2.example.json should exist in project root"
