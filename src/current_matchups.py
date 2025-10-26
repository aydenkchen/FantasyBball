"""Display current week's matchups with mid-week scores.

Usage:
    python -m src.current_matchups
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa


def parse_team_stats(team_data):
    """Extract stats from team data structure."""
    stats = {}

    # team_data is a list with two elements:
    # [0] = list of dicts with metadata (team_key, name, etc.)
    # [1] = dict with team_stats, team_points, etc.

    if not isinstance(team_data, list) or len(team_data) < 2:
        return stats

    # Get the second element which contains team_stats
    stats_container = team_data[1]

    if not isinstance(stats_container, dict) or 'team_stats' not in stats_container:
        return stats

    team_stats = stats_container['team_stats']

    if 'stats' not in team_stats:
        return stats

    # Parse each stat
    stat_map = {
        '9004003': 'fgm_fga',
        '5': 'fg_pct',
        '9007006': 'ftm_fta',
        '8': 'ft_pct',
        '10': '3ptm',
        '12': 'pts',
        '15': 'reb',
        '16': 'ast',
        '17': 'st',
        '18': 'blk',
        '19': 'to'
    }

    for stat_item in team_stats['stats']:
        stat = stat_item['stat']
        stat_id = stat['stat_id']
        if stat_id in stat_map:
            stats[stat_map[stat_id]] = stat['value']

    return stats


def get_team_name(team_data):
    """Extract team name from team data."""
    # team_data[0] is a list of dicts with metadata
    if not isinstance(team_data, list) or len(team_data) < 1:
        return "Unknown Team"

    metadata = team_data[0]
    if not isinstance(metadata, list):
        return "Unknown Team"

    for item in metadata:
        if isinstance(item, dict) and 'name' in item:
            return item['name']

    return "Unknown Team"


def get_team_key(team_data):
    """Extract team key from team data."""
    if not isinstance(team_data, list) or len(team_data) < 1:
        return None

    metadata = team_data[0]
    if not isinstance(metadata, list):
        return None

    for item in metadata:
        if isinstance(item, dict) and 'team_key' in item:
            return item['team_key']

    return None


def compare_stats(team1_stats, team2_stats):
    """Compare two teams' stats and determine category winners."""
    categories = [
        ('fg_pct', 'FG%', 'higher'),
        ('ft_pct', 'FT%', 'higher'),
        ('3ptm', '3PTM', 'higher'),
        ('pts', 'PTS', 'higher'),
        ('reb', 'REB', 'higher'),
        ('ast', 'AST', 'higher'),
        ('st', 'ST', 'higher'),
        ('blk', 'BLK', 'higher'),
        ('to', 'TO', 'lower'),  # Lower is better for turnovers
    ]

    team1_wins = 0
    team2_wins = 0
    results = []

    for stat_key, display_name, direction in categories:
        if stat_key not in team1_stats or stat_key not in team2_stats:
            results.append((display_name, 'N/A', 'N/A', '-'))
            continue

        val1 = float(team1_stats[stat_key])
        val2 = float(team2_stats[stat_key])

        if direction == 'higher':
            if val1 > val2:
                winner = '←'
                team1_wins += 1
            elif val2 > val1:
                winner = '→'
                team2_wins += 1
            else:
                winner = 'TIE'
        else:  # lower is better
            if val1 < val2:
                winner = '←'
                team1_wins += 1
            elif val2 < val1:
                winner = '→'
                team2_wins += 1
            else:
                winner = 'TIE'

        results.append((display_name, val1, val2, winner))

    return team1_wins, team2_wins, results


def display_matchup(matchup_num, matchup_data):
    """Display a single matchup with scores."""
    # Navigate the nested structure
    if 'matchup' not in matchup_data:
        return

    matchup = matchup_data['matchup']

    # Get teams from the nested structure
    # matchup['0']['teams'] contains the two teams
    if '0' not in matchup or 'teams' not in matchup['0']:
        return

    teams = matchup['0']['teams']

    # Extract team data
    team1_data = teams.get('0', {}).get('team', [])
    team2_data = teams.get('1', {}).get('team', [])

    team1_name = get_team_name(team1_data)
    team2_name = get_team_name(team2_data)

    team1_stats = parse_team_stats(team1_data)
    team2_stats = parse_team_stats(team2_data)

    # Compare stats
    team1_wins, team2_wins, results = compare_stats(team1_stats, team2_stats)

    # Display header
    print("=" * 100)
    print(f"MATCHUP {matchup_num}")
    print(f"{team1_name} vs {team2_name}")
    print(f"Current Score: {team1_name} {team1_wins} - {team2_wins} {team2_name}")
    print("=" * 100)

    # Display category breakdown
    print(f"{'Category':<10} {team1_name[:18]:<20} {team2_name[:18]:<20} {'Winner':<10}")
    print("-" * 100)

    for display_name, val1, val2, winner in results:
        val1_str = f"{val1}" if val1 != 'N/A' else 'N/A'
        val2_str = f"{val2}" if val2 != 'N/A' else 'N/A'

        print(f"{display_name:<10} {val1_str:<20} {val2_str:<20} {winner:<10}")

    print()


def main():
    # Authenticate
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    # Get current week
    current_week = lg.current_week()
    print(f"\n{'=' * 100}")
    print(f"CURRENT WEEK: Week {current_week} - MID-WEEK MATCHUP SCORES")
    print(f"{'=' * 100}\n")

    # Get matchups for current week
    matchups = lg.matchups(week=current_week)

    # Display each matchup
    matchup_num = 1
    for matchup_key, matchup_data in matchups.items():
        display_matchup(matchup_num, matchup_data)
        matchup_num += 1

    print("=" * 100)
    print("Legend:")
    print("  ← = Team 1 (left) is winning this category")
    print("  → = Team 2 (right) is winning this category")
    print("  TO (Turnovers): Lower is better")
    print("=" * 100)


if __name__ == '__main__':
    main()
