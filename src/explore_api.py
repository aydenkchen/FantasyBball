"""Explore Yahoo Fantasy API data structure and query options.

Usage:
    python -m src.explore_api
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json


def explore_league_data():
    """Explore what data is available from the league."""
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    print("=" * 80)
    print("LEAGUE SETTINGS")
    print("=" * 80)
    settings = lg.settings()
    print(json.dumps(settings, indent=2))
    print()

    print("=" * 80)
    print("STAT CATEGORIES")
    print("=" * 80)
    stat_categories = lg.stat_categories()
    print(json.dumps(stat_categories, indent=2))
    print()

    return lg


def explore_team_data(lg):
    """Explore what data is available for teams."""
    print("=" * 80)
    print("TEAMS")
    print("=" * 80)
    teams = lg.teams()
    for team_key, team_data in teams.items():
        print(f"\nTeam Key: {team_key}")
        print(json.dumps(team_data, indent=2))
        break  # Just show first team structure
    print()

    # Get first team for detailed exploration
    first_team_key = list(teams.keys())[0]
    team = lg.to_team(first_team_key)

    print("=" * 80)
    print("TEAM ROSTER")
    print("=" * 80)
    roster = team.roster()
    print(json.dumps(roster[:2], indent=2))  # Show first 2 players
    print(f"... ({len(roster)} total players)")
    print()

    print("=" * 80)
    print("TEAM STATS (Season)")
    print("=" * 80)
    try:
        stats = team.stats('season')
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Error getting team stats: {e}")
    print()

    print("=" * 80)
    print("TEAM STATS (Week 1)")
    print("=" * 80)
    try:
        stats = team.stats('week', week=1)
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Error getting week stats: {e}")
    print()

    return team


def explore_matchup_data(lg):
    """Explore matchup data."""
    print("=" * 80)
    print("MATCHUPS (Week 1)")
    print("=" * 80)
    try:
        matchups = lg.matchups(week=1)
        print(json.dumps(matchups, indent=2))
    except Exception as e:
        print(f"Error getting matchups: {e}")
    print()

    print("=" * 80)
    print("CURRENT WEEK MATCHUPS")
    print("=" * 80)
    try:
        matchups = lg.matchups()
        print(json.dumps(matchups, indent=2))
    except Exception as e:
        print(f"Error getting current matchups: {e}")
    print()


def explore_scoreboard(lg):
    """Explore scoreboard data."""
    print("=" * 80)
    print("SCOREBOARD (Week 1)")
    print("=" * 80)
    try:
        scoreboard = lg.scoreboard(week=1)
        print(json.dumps(scoreboard, indent=2))
    except Exception as e:
        print(f"Error getting scoreboard: {e}")
    print()


def explore_standings(lg):
    """Explore standings data."""
    print("=" * 80)
    print("STANDINGS")
    print("=" * 80)
    try:
        standings = lg.standings()
        print(json.dumps(standings[:2], indent=2))  # First 2 teams
        print(f"... ({len(standings)} total teams)")
    except Exception as e:
        print(f"Error getting standings: {e}")
    print()


def main():
    print("\n" + "=" * 80)
    print("YAHOO FANTASY API EXPLORATION")
    print("=" * 80 + "\n")

    lg = explore_league_data()
    explore_standings(lg)
    explore_team_data(lg)
    explore_matchup_data(lg)
    explore_scoreboard(lg)

    print("\n" + "=" * 80)
    print("EXPLORATION COMPLETE")
    print("=" * 80)
    print("\nReview the output above to understand:")
    print("1. What stat categories are tracked")
    print("2. What data is available per team")
    print("3. Whether stats are available by week or cumulative")
    print("4. What matchup/scoreboard data looks like")
    print("5. Best way to structure data queries")


if __name__ == '__main__':
    main()
