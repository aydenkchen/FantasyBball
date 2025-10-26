"""Debug script to see the actual matchup data structure.

Usage:
    python -m src.debug_matchups
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json


def main():
    # Authenticate
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    # Get current week
    current_week = lg.current_week()
    print(f"Current week: {current_week}\n")

    # Get matchups for current week
    matchups = lg.matchups(week=current_week)

    print(f"Type of matchups: {type(matchups)}")
    print(f"Number of matchups: {len(matchups)}")
    print(f"Matchup keys: {list(matchups.keys())}\n")

    # Show structure of first matchup
    if matchups:
        first_key = list(matchups.keys())[0]
        print(f"First matchup key: {first_key}")
        print(f"First matchup type: {type(matchups[first_key])}")
        print("\nFirst matchup structure (top level keys):")
        if isinstance(matchups[first_key], dict):
            for key in matchups[first_key].keys():
                print(f"  - {key}")

        print("\n" + "="*80)
        print("FULL FIRST MATCHUP DATA:")
        print("="*80)
        print(json.dumps(matchups[first_key], indent=2, default=str))


if __name__ == '__main__':
    main()
