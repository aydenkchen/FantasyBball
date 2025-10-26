"""Quick test scripts to list NBA leagues for 2025 using yahoo-fantasy-api.

Usage:
    python -m src.quick_test

Fill `oauth2.json` in the project root before running.
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import logging
import json
import os


def list_leagues_via_yfa(from_file: str = 'oauth2.json', year: int = 2025):
    if not os.path.exists(from_file):
        raise FileNotFoundError(f"OAuth credentials file not found: {from_file}")

    # Validate year parameter
    current_year = 2025  # Update this as needed
    if year < 2000 or year > current_year + 1:
        raise ValueError(f"Invalid year: {year}. Must be between 2000 and {current_year + 1}")

    sc = OAuth2(None, None, from_file=from_file)
    if not sc.token_is_valid():
        logging.info('Token invalid; refreshing (this may open a browser for first-time auth).')
        sc.refresh_access_token()

    gm = yfa.Game(sc, 'nba')
    leagues = gm.league_ids(year=year)
    return leagues


def main():
    try:
        leagues = list_leagues_via_yfa('oauth2.json', 2025)
        print('Found league IDs:', leagues)
    except Exception as e:
        print('Error listing leagues with yahoo-fantasy-api:', e)


if __name__ == '__main__':
    main()
