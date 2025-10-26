"""Simple OAuth helper using yahoo_oauth.

Place your `oauth2.json` (with consumer_key and consumer_secret) in the project root.
Run this to perform the first-time authorization which opens a browser.
"""

from yahoo_oauth import OAuth2
import logging
import os


def get_oauth(from_file: str = "oauth2.json") -> OAuth2:
    """Create and return an OAuth2 object using the provided credentials file.

    Args:
        from_file: Path to the oauth2.json file (relative to project root by default).

    Returns:
        OAuth2 instance (may open a browser on first run to authorize).
    """
    if not os.path.exists(from_file):
        raise FileNotFoundError(f"OAuth credentials file not found: {from_file}")

    # oauth2 library will manage token storage automatically (in ~/.config or token file)
    sc = OAuth2(None, None, from_file=from_file)
    if not sc.token_is_valid():
        logging.info("OAuth token not valid; this will open a browser to authorize.")
        sc.refresh_access_token()

    return sc


if __name__ == "__main__":
    import sys

    try:
        sc = get_oauth(sys.argv[1] if len(sys.argv) > 1 else "oauth2.json")
        print("OAuth setup complete. Token valid:", sc.token_is_valid())
    except Exception as e:
        print("Error during OAuth setup:", e)
