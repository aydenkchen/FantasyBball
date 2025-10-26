"""Understand yahoo_fantasy_api capabilities for stats retrieval.

Usage:
    python -m src.api_capabilities
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json


def test_stat_categories(lg):
    """What stat categories are tracked?"""
    print("=" * 80)
    print("STAT CATEGORIES")
    print("=" * 80)
    stats = lg.stat_categories()
    for stat in stats:
        print(f"  {stat}")
    print()


def test_matchup_structure(lg):
    """What does matchup data look like?"""
    print("=" * 80)
    print("MATCHUP DATA STRUCTURE (Week 1)")
    print("=" * 80)
    matchups = lg.matchups(week=1)

    # Show first matchup in detail
    if matchups and len(matchups) > 0:
        first_matchup = matchups[list(matchups.keys())[0]]
        print("First matchup structure:")
        print(json.dumps(first_matchup, indent=2, default=str))
    print()


def test_team_stats_availability(lg):
    """Can we get team stats? Weekly vs season?"""
    print("=" * 80)
    print("TEAM STATS AVAILABILITY")
    print("=" * 80)

    teams = lg.teams()
    first_team_key = list(teams.keys())[0]
    team = lg.to_team(first_team_key)

    print(f"Testing with team: {teams[first_team_key]['name']}")
    print()

    # Try different stat requests
    print("Available Team methods:")
    team_methods = [m for m in dir(team) if not m.startswith('_')]
    for method in team_methods:
        print(f"  - {method}")
    print()


def test_standings_detail(lg):
    """What's in the standings data?"""
    print("=" * 80)
    print("STANDINGS DATA STRUCTURE")
    print("=" * 80)
    standings = lg.standings()

    if standings and len(standings) > 0:
        print("First team in standings:")
        print(json.dumps(standings[0], indent=2, default=str))
    print()


def test_league_methods(lg):
    """List all available league methods."""
    print("=" * 80)
    print("AVAILABLE LEAGUE METHODS")
    print("=" * 80)
    league_methods = [m for m in dir(lg) if not m.startswith('_')]
    for method in league_methods:
        print(f"  - {method}")
    print()


def main():
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    print("\n" + "=" * 80)
    print("YAHOO FANTASY API CAPABILITIES TEST")
    print("=" * 80 + "\n")

    test_league_methods(lg)
    test_stat_categories(lg)
    test_standings_detail(lg)
    test_matchup_structure(lg)
    test_team_stats_availability(lg)

    print("=" * 80)
    print("KEY QUESTIONS TO ANSWER:")
    print("=" * 80)
    print("1. Does matchups() include weekly stats for each team?")
    print("2. Are FGM/FGA and FTM/FTA available separately?")
    print("3. Can we get cumulative stats through a specific week?")
    print("4. Can we get just one week's stats (not cumulative)?")
    print()


if __name__ == '__main__':
    main()
