"""Quick script to show team names from API.

Usage:
    python -m src.show_team_names
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa


def get_team_name(team_data):
    """Extract team name from team data."""
    if not isinstance(team_data, list) or len(team_data) < 1:
        return "Unknown Team"

    metadata = team_data[0]
    if not isinstance(metadata, list):
        return "Unknown Team"

    for item in metadata:
        if isinstance(item, dict) and 'name' in item:
            return item['name']

    return "Unknown Team"


def main():
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    raw_matchups = lg.matchups(week=1)
    league_data = raw_matchups['fantasy_content']['league']
    scoreboard = league_data[1]['scoreboard']
    matchups_container = scoreboard['0']['matchups']

    teams = []
    matchup_count = int(matchups_container['count'])

    for i in range(matchup_count):
        matchup_data = matchups_container[str(i)]
        matchup_teams = matchup_data['matchup']['0']['teams']

        for team_idx in ['0', '1']:
            team_data = matchup_teams[team_idx]['team']
            team_name = get_team_name(team_data)
            teams.append(team_name)

    print("Team names from API:")
    for i, name in enumerate(teams, 1):
        print(f"{i:2}. {name}")
        print(f"    First 4 chars: '{name[:4]}'")


if __name__ == '__main__':
    main()
