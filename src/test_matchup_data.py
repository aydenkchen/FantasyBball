"""Test what data structure matchups() returns.

Usage:
    python -m src.test_matchup_data
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json


def main():
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    print("=" * 80)
    print("TESTING MATCHUP DATA STRUCTURE")
    print("=" * 80)
    print()

    # Get matchups for week 1
    print("Week 1 Matchups:")
    print("-" * 80)
    matchups = lg.matchups(week=1)

    # Pretty print the structure
    print(json.dumps(matchups, indent=2, default=str))
    print()

    print("=" * 80)
    print("STAT CATEGORIES")
    print("=" * 80)
    stats = lg.stat_categories()
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
