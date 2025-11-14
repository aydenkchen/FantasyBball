"""Generate the full Possibility Matrix - showing how every team would perform against every other team.

This recreates the Excel "Possibility Matrix" concept in Python, showing all N×N possible matchup results
for a given week, not just the scheduled matchups.

Usage:
    python -m src.possibility_matrix
    python -m src.possibility_matrix --week 1
"""
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import argparse


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
                    if stat_value and stat_value.strip():
                        try:
                            processed_stats[stat_key] = float(stat_value)
                        except ValueError:
                            processed_stats[stat_key] = 0.0
                    else:
                        processed_stats[stat_key] = 0.0

            teams[team_name] = processed_stats

    return teams


def compare_two_teams(team1_stats, team2_stats):
    """Compare two teams and return (team1_wins, team2_wins).

    Returns tuple of (categories won by team1, categories won by team2)
    """
    categories = [
        ('fg_pct', 'higher'),
        ('ft_pct', 'higher'),
        ('3ptm', 'higher'),
        ('pts', 'higher'),
        ('reb', 'higher'),
        ('ast', 'higher'),
        ('st', 'higher'),
        ('blk', 'higher'),
        ('to', 'lower'),  # Lower is better for turnovers
    ]

    team1_wins = 0
    team2_wins = 0

    for stat_key, direction in categories:
        if stat_key not in team1_stats or stat_key not in team2_stats:
            continue

        val1 = team1_stats[stat_key]
        val2 = team2_stats[stat_key]

        if direction == 'higher':
            if val1 > val2:
                team1_wins += 1
            elif val2 > val1:
                team2_wins += 1
            # else: tie, no one gets a point
        else:  # lower is better
            if val1 < val2:
                team1_wins += 1
            elif val2 < val1:
                team2_wins += 1

    return team1_wins, team2_wins


def generate_possibility_matrix(teams):
    """Generate the full N×N possibility matrix.

    Returns: dict of {team1_name: {team2_name: "X-Y"}}
    """
    matrix = {}
    team_names = list(teams.keys())

    for team1_name in team_names:
        matrix[team1_name] = {}
        for team2_name in team_names:
            if team1_name == team2_name:
                # Team vs itself
                matrix[team1_name][team2_name] = "-"
            else:
                # Calculate matchup
                team1_wins, team2_wins = compare_two_teams(teams[team1_name], teams[team2_name])
                matrix[team1_name][team2_name] = f"{team1_wins}-{team2_wins}"

    return matrix


def display_possibility_matrix(matrix, week):
    """Display the possibility matrix in a formatted table with color coding."""
    team_names = list(matrix.keys())

    # ANSI color codes
    GREEN = '\033[92m'   # Win (> 4.5 categories)
    RED = '\033[91m'     # Loss (< 4.5 categories)
    YELLOW = '\033[93m'  # Tie (= 4.5 categories)
    BOLD = '\033[1m'
    RESET = '\033[0m'

    # Determine column width for team names (max 28 chars)
    col_width = 28
    total_width = col_width + 3 + (len(team_names) * 5)  # name + " │ " + results

    print(f"\n{BOLD}{'═' * total_width}{RESET}")
    print(f"{BOLD}WEEK {week} - POSSIBILITY MATRIX{RESET}")
    print(f"Shows how each team (rows) would perform against every other team (columns)")
    print(f"{BOLD}{'═' * total_width}{RESET}\n")

    # Prepare truncated team names for headers
    team_headers = []
    for name in team_names:
        if len(name) > col_width:
            team_headers.append(name[:col_width])
        else:
            team_headers.append(name)

    # Print column headers (rotated team names)
    # We'll print the header as full team names vertically-aligned
    header_line1 = " " * (col_width + 3) + "│"
    for team_header in team_headers:
        header_line1 += f" {team_header[:4]:^4}"

    # Create custom abbreviations for column headers
    abbreviations = {
        "Edey is the new Jokić": "Edey",
        "Ivica Zubat": "Ivic",
        "Will's Groovy Team": "Will",
        "Ben's Best Team": "BenB",
        "Aidan's Legacy Squad": "Kurt",
        "The Real Slim Shai'dy": "Dani",
        "Basketball makes me Nembhard": "Aden",
        "Ben's Glorious Team": "BenG",
        "BK's Big Ballers": "BK",
        "Zach's Amazing Team": "Zach"
    }

    # Print team name headers across the top
    print(f"{BOLD}{'vs →':<{col_width}} │{RESET}", end="")
    for team_header in team_headers:
        # Use custom abbreviation or fallback to first 4 chars
        short_name = abbreviations.get(team_header, team_header[:4].strip())
        print(f"{BOLD} {short_name:^4}{RESET}", end="")
    print()
    print(f"{BOLD}{'─' * total_width}{RESET}")

    # Each team's row
    for i, team_name in enumerate(team_names, 1):
        # Truncate long team names
        display_name = team_name[:col_width] if len(team_name) > col_width else team_name
        row = f"{display_name:<{col_width}} │"

        for opponent_name in team_names:
            result = matrix[team_name][opponent_name]

            if result == "-":
                # Team vs itself
                row += f" {result:^4}"
            else:
                # Color code based on win/loss
                wins, losses = map(int, result.split('-'))
                if wins > losses:
                    # Win
                    row += f" {GREEN}{result:^4}{RESET}"
                elif losses > wins:
                    # Loss
                    row += f" {RED}{result:^4}{RESET}"
                else:
                    # Tie (rare but possible)
                    row += f" {YELLOW}{result:^4}{RESET}"

        print(row)

    # Legend
    print(f"\n{BOLD}{'═' * total_width}{RESET}")
    print(f"{BOLD}FULL TEAM NAMES:{RESET}")
    for i, team_name in enumerate(team_names, 1):
        print(f"  {i:2}. {team_name}")

    print(f"\n{BOLD}COLOR CODING:{RESET}")
    print(f"  {GREEN}Green{RESET} = Win (won more categories)")
    print(f"  {RED}Red{RESET}   = Loss (lost more categories)")
    print(f"  {YELLOW}Yellow{RESET} = Tie (equal categories, rare)")
    print(f"  - = Team vs itself")
    print(f"{BOLD}{'═' * total_width}{RESET}")


def analyze_matrix_insights(matrix, teams):
    """Analyze the possibility matrix for insights."""
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    print(f"\n{BOLD}{'═' * 140}{RESET}")
    print(f"{BOLD}POSSIBILITY MATRIX INSIGHTS{RESET}")
    print(f"{BOLD}{'═' * 140}{RESET}\n")

    team_names = list(matrix.keys())

    # Calculate overall record if each team played everyone
    overall_records = {}

    for team_name in team_names:
        total_wins = 0
        total_losses = 0

        for opponent_name in team_names:
            if opponent_name == team_name:
                continue

            result = matrix[team_name][opponent_name]
            if result != "-":
                wins, losses = map(int, result.split('-'))
                total_wins += wins
                total_losses += losses

        overall_records[team_name] = {
            'total_wins': total_wins,
            'total_losses': total_losses,
            'win_pct': total_wins / (total_wins + total_losses) if (total_wins + total_losses) > 0 else 0
        }

    # Sort by win percentage
    sorted_teams = sorted(overall_records.items(), key=lambda x: x[1]['win_pct'], reverse=True)

    print(f"{BOLD}OVERALL STRENGTH RANKINGS{RESET} (if each team played all 9 opponents):")
    print(f"{BOLD}{'─' * 90}{RESET}")
    print(f"{'Rank':<6} {'Team':<35} {'Cats Won':<12} {'Cats Lost':<12} {'Win %':<10}")
    print(f"{'─' * 90}")

    for rank, (team_name, record) in enumerate(sorted_teams, 1):
        team_display = team_name[:33]
        win_pct_str = f"{record['win_pct']:.1%}"

        # Highlight top 3 teams
        if rank <= 3:
            print(f"{GREEN}{rank:<6} {team_display:<35} {record['total_wins']:<12} {record['total_losses']:<12} {win_pct_str:<10}{RESET}")
        else:
            print(f"{rank:<6} {team_display:<35} {record['total_wins']:<12} {record['total_losses']:<12} {win_pct_str:<10}")

    # Best and worst matchups for each team
    print(f"\n{BOLD}{'═' * 140}{RESET}")
    print(f"{BOLD}BEST AND WORST MATCHUPS PER TEAM{RESET}")
    print(f"{BOLD}{'═' * 140}{RESET}\n")

    for team_name in team_names:
        matchups = []
        for opponent_name in team_names:
            if opponent_name == team_name:
                continue
            result = matrix[team_name][opponent_name]
            wins, losses = map(int, result.split('-'))
            matchups.append((opponent_name, wins, losses, wins - losses))

        # Sort by margin
        matchups.sort(key=lambda x: x[3], reverse=True)

        best = matchups[0]
        worst = matchups[-1]

        team_display = team_name[:40]
        best_opponent = best[0][:35]
        worst_opponent = worst[0][:35]

        print(f"{BOLD}{team_display}{RESET}")
        print(f"  {GREEN}Best:{RESET}  vs {best_opponent:<35} ({best[1]}-{best[2]}, +{best[3]} margin)")
        print(f"  {RED}Worst:{RESET} vs {worst_opponent:<35} ({worst[1]}-{worst[2]}, {worst[3]:+d} margin)")
        print()


def main():
    parser = argparse.ArgumentParser(description='Generate Possibility Matrix for a given week')
    parser.add_argument('--week', type=int, default=1, help='Week number (default: 1)')
    args = parser.parse_args()

    # Authenticate
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    print(f"Fetching data for Week {args.week}...")

    # Get matchups for specified week
    try:
        raw_matchups = lg.matchups(week=args.week)
    except Exception as e:
        print(f"Error fetching week {args.week} data: {e}")
        print("Try a different week number.")
        return

    # Navigate to the actual matchups data
    league_data = raw_matchups['fantasy_content']['league']
    scoreboard = league_data[1]['scoreboard']
    matchups_container = scoreboard['0']['matchups']

    # Extract all 10 teams
    teams = extract_all_teams(matchups_container)

    if not teams or len(teams) == 0:
        print(f"No data found for Week {args.week}. The week may not have started yet.")
        return

    print(f"Found {len(teams)} teams with data.\n")

    # Generate the possibility matrix
    matrix = generate_possibility_matrix(teams)

    # Display the matrix
    display_possibility_matrix(matrix, args.week)

    # Analyze insights
    analyze_matrix_insights(matrix, teams)


if __name__ == '__main__':
    main()
