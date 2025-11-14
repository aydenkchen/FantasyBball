"""Display category rankings matrix - each team's rank (1-10) in each stat category.

Usage:
    python -m src.category_rankings [--week WEEK_NUM]

Examples:
    python -m src.category_rankings              # Current week
    python -m src.category_rankings --week 5     # Specific week
"""
import argparse
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa


def parse_team_stats(team_data):
    """Extract stats from team data structure."""
    stats = {}

    if not isinstance(team_data, list) or len(team_data) < 2:
        return stats

    stats_container = team_data[1]

    if not isinstance(stats_container, dict) or 'team_stats' not in stats_container:
        return stats

    team_stats = stats_container['team_stats']

    if 'stats' not in team_stats:
        return stats

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
    if not isinstance(team_data, list) or len(team_data) < 1:
        return "Unknown Team"

    metadata = team_data[0]
    if not isinstance(metadata, list):
        return "Unknown Team"

    for item in metadata:
        if isinstance(item, dict) and 'name' in item:
            return item['name']

    return "Unknown Team"


def extract_all_teams(matchups_container):
    """Extract all 10 teams from the 5 matchups."""
    teams = {}

    matchup_count = int(matchups_container['count'])

    for i in range(matchup_count):
        matchup_data = matchups_container[str(i)]
        matchup_teams = matchup_data['matchup']['0']['teams']

        # Get both teams from this matchup
        for team_idx in ['0', '1']:
            team_data = matchup_teams[team_idx]['team']
            team_name = get_team_name(team_data)
            team_stats = parse_team_stats(team_data)

            # Convert stats to floats
            processed_stats = {}
            for stat_key, stat_value in team_stats.items():
                if stat_key in ['fg_pct', 'ft_pct', '3ptm', 'pts', 'reb', 'ast', 'st', 'blk', 'to']:
                    processed_stats[stat_key] = float(stat_value)

            teams[team_name] = processed_stats

    return teams


def rank_teams_by_category(teams):
    """Rank all teams (1-10) for each stat category.

    Returns: dict of {team_name: {stat_category: rank}}
    """
    categories = {
        'fg_pct': ('FG%', 'higher'),
        'ft_pct': ('FT%', 'higher'),
        '3ptm': ('3PTM', 'higher'),
        'pts': ('PTS', 'higher'),
        'reb': ('REB', 'higher'),
        'ast': ('AST', 'higher'),
        'st': ('ST', 'higher'),
        'blk': ('BLK', 'higher'),
        'to': ('TO', 'lower'),  # Lower is better
    }

    rankings = {team_name: {} for team_name in teams.keys()}

    for stat_key, (display_name, direction) in categories.items():
        # Sort teams by this stat
        if direction == 'higher':
            sorted_teams = sorted(teams.items(), key=lambda x: x[1].get(stat_key, 0), reverse=True)
        else:  # lower is better
            sorted_teams = sorted(teams.items(), key=lambda x: x[1].get(stat_key, float('inf')))

        # Assign ranks
        for rank, (team_name, _) in enumerate(sorted_teams, start=1):
            rankings[team_name][stat_key] = rank

    return rankings


def calculate_average_rank(team_rankings):
    """Calculate average rank across all categories for each team."""
    avg_ranks = {}
    for team_name, ranks in team_rankings.items():
        avg_rank = sum(ranks.values()) / len(ranks)
        avg_ranks[team_name] = avg_rank
    return avg_ranks


def display_rankings_matrix(teams, rankings, week):
    """Display the 10x9 rankings matrix."""
    print(f"\n{'=' * 110}")
    print(f"WEEK {week} - CATEGORY RANKINGS MATRIX (1=Best, 10=Worst)")
    print(f"{'=' * 110}")

    # Header
    header = f"{'Team Name':<30} | {'FG%':>4} {'FT%':>4} {'3PTM':>4} {'PTS':>4} {'REB':>4} {'AST':>4} {'ST':>4} {'BLK':>4} {'TO':>4} | {'Avg':>4}"
    print(header)
    print("-" * 110)

    # Calculate average ranks for sorting
    avg_ranks = calculate_average_rank(rankings)

    # Sort teams by average rank (best overall teams first)
    sorted_teams = sorted(rankings.items(), key=lambda x: avg_ranks[x[0]])

    # Display each team
    for team_name, ranks in sorted_teams:
        avg_rank = avg_ranks[team_name]

        # Truncate long team names
        display_name = team_name[:28] if len(team_name) > 28 else team_name

        row = f"{display_name:<30} |"
        row += f" {ranks.get('fg_pct', '-'):>4}"
        row += f" {ranks.get('ft_pct', '-'):>4}"
        row += f" {ranks.get('3ptm', '-'):>4}"
        row += f" {ranks.get('pts', '-'):>4}"
        row += f" {ranks.get('reb', '-'):>4}"
        row += f" {ranks.get('ast', '-'):>4}"
        row += f" {ranks.get('st', '-'):>4}"
        row += f" {ranks.get('blk', '-'):>4}"
        row += f" {ranks.get('to', '-'):>4}"
        row += f" | {avg_rank:>4.1f}"

        print(row)

    print("=" * 110)
    print("Legend:")
    print("  1 = Best in category, 10 = Worst in category")
    print("  TO (Turnovers): 1 = Fewest (best), 10 = Most (worst)")
    print("  Avg = Average rank across all 9 categories")
    print("=" * 110)


def display_detailed_rankings(teams, rankings, week):
    """Display rankings with actual stat values."""
    print(f"\n{'=' * 130}")
    print(f"WEEK {week} - DETAILED CATEGORY RANKINGS")
    print(f"{'=' * 130}")

    categories = [
        ('fg_pct', 'FG%', 'higher'),
        ('ft_pct', 'FT%', 'higher'),
        ('3ptm', '3PTM', 'higher'),
        ('pts', 'PTS', 'higher'),
        ('reb', 'REB', 'higher'),
        ('ast', 'AST', 'higher'),
        ('st', 'ST', 'higher'),
        ('blk', 'BLK', 'higher'),
        ('to', 'TO', 'lower'),
    ]

    for stat_key, display_name, direction in categories:
        print(f"\n{display_name} Rankings {'(Lower is Better)' if direction == 'lower' else ''}:")
        print("-" * 60)

        # Sort teams by this stat
        if direction == 'higher':
            sorted_teams = sorted(teams.items(), key=lambda x: x[1].get(stat_key, 0), reverse=True)
        else:
            sorted_teams = sorted(teams.items(), key=lambda x: x[1].get(stat_key, float('inf')))

        # Display
        for rank, (team_name, team_stats) in enumerate(sorted_teams, start=1):
            stat_value = team_stats.get(stat_key, 0)
            team_display = team_name[:35]
            print(f"  {rank:2}. {team_display:<35} {stat_value:>8}")


def analyze_category_strengths(rankings):
    """Identify each team's category strengths and weaknesses."""
    print(f"\n{'=' * 130}")
    print(f"CATEGORY STRENGTH ANALYSIS")
    print(f"{'=' * 130}")

    for team_name, ranks in rankings.items():
        # Find strengths (rank 1-3) and weaknesses (rank 8-10)
        strengths = []
        weaknesses = []

        cat_names = {
            'fg_pct': 'FG%', 'ft_pct': 'FT%', '3ptm': '3PTM',
            'pts': 'PTS', 'reb': 'REB', 'ast': 'AST',
            'st': 'ST', 'blk': 'BLK', 'to': 'TO'
        }

        for stat_key, rank in ranks.items():
            if rank <= 3:
                strengths.append(f"{cat_names[stat_key]} (#{rank})")
            elif rank >= 8:
                weaknesses.append(f"{cat_names[stat_key]} (#{rank})")

        print(f"\n{team_name}")
        print(f"  Strengths: {', '.join(strengths) if strengths else 'None in top 3'}")
        print(f"  Weaknesses: {', '.join(weaknesses) if weaknesses else 'None in bottom 3'}")


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Display category rankings matrix for all teams'
    )
    parser.add_argument(
        '--week', '-w',
        type=int,
        default=None,
        help='Week number (default: current week)'
    )
    args = parser.parse_args()

    # Authenticate
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    # Get week to analyze
    week = args.week if args.week else lg.current_week()

    # Get matchups for specified week
    raw_matchups = lg.matchups(week=week)

    # Navigate to the actual matchups data
    league_data = raw_matchups['fantasy_content']['league']
    scoreboard = league_data[1]['scoreboard']
    matchups_container = scoreboard['0']['matchups']

    # Extract all 10 teams
    teams = extract_all_teams(matchups_container)

    # Rank teams in each category
    rankings = rank_teams_by_category(teams)

    # Display rankings matrix
    display_rankings_matrix(teams, rankings, week)

    # Display detailed rankings
    display_detailed_rankings(teams, rankings, week)

    # Analyze strengths/weaknesses
    analyze_category_strengths(rankings)


if __name__ == '__main__':
    main()
