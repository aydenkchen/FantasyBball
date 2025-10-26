"""Fetch and display league data using yahoo-fantasy-api.

Usage:
    python -m src.league_data
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa


def main():
    # Authenticate
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')

    # Your league ID
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    print("=" * 60)
    print("LEAGUE SETTINGS")
    print("=" * 60)
    settings = lg.settings()
    print(f"League Name: {settings.get('name')}")
    print(f"Season: {settings.get('season')}")
    print(f"Num Teams: {settings.get('num_teams')}")
    print(f"Scoring Type: {settings.get('scoring_type')}")
    print()

    print("=" * 60)
    print("STANDINGS")
    print("=" * 60)
    standings = lg.standings()
    for team in standings:
        print(f"{team['name']}: {team.get('outcome_totals', {}).get('wins', 0)}-{team.get('outcome_totals', {}).get('losses', 0)}")
    print()

    print("=" * 60)
    print("YOUR TEAM(S)")
    print("=" * 60)
    teams = lg.teams()
    for team_key, team_data in teams.items():
        print(f"Team: {team_data['name']}")
        print(f"Team Key: {team_key}")
    print()

    print("=" * 60)
    print("FREE AGENTS (Top 10 by rank)")
    print("=" * 60)
    # Get top free agents
    free_agents = lg.free_agents('G')  # Guards
    for i, player in enumerate(free_agents[:10], 1):
        print(f"{i}. {player.get('name', 'Unknown')} - {player.get('position_type', 'N/A')}")
    print()


if __name__ == '__main__':
    main()
