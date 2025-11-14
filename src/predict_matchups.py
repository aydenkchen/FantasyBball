"""Predict matchup results using historical data.

Usage:
    python -m src.predict_matchups --method last --week 2
    python -m src.predict_matchups --method last3
    python -m src.predict_matchups --method total

Methods:
    last  - Based on last week's performance
    last3 - Based on average of last 3 weeks
    total - Based on season total average
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
        '5': 'fg_pct',
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


def extract_matchups(matchups_container):
    """Extract scheduled matchups (team pairs) for the week."""
    matchups = []
    matchup_count = int(matchups_container['count'])

    for i in range(matchup_count):
        matchup_data = matchups_container[str(i)]
        matchup_teams = matchup_data['matchup']['0']['teams']

        team1_data = matchup_teams['0']['team']
        team2_data = matchup_teams['1']['team']

        team1_name = get_team_name(team1_data)
        team2_name = get_team_name(team2_data)
        team1_key = get_team_key(team1_data)
        team2_key = get_team_key(team2_data)

        matchups.append({
            'team1_name': team1_name,
            'team2_name': team2_name,
            'team1_key': team1_key,
            'team2_key': team2_key
        })

    return matchups


def extract_all_teams_stats(matchups_container):
    """Extract all team stats from matchups."""
    teams = {}
    matchup_count = int(matchups_container['count'])

    for i in range(matchup_count):
        matchup_data = matchups_container[str(i)]
        matchup_teams = matchup_data['matchup']['0']['teams']

        for team_idx in ['0', '1']:
            team_data = matchup_teams[team_idx]['team']
            team_key = get_team_key(team_data)
            team_stats = parse_team_stats(team_data)

            # Convert stats to floats
            processed_stats = {}
            for stat_key, stat_value in team_stats.items():
                if stat_value and stat_value.strip():
                    try:
                        processed_stats[stat_key] = float(stat_value)
                    except ValueError:
                        processed_stats[stat_key] = 0.0
                else:
                    processed_stats[stat_key] = 0.0

            teams[team_key] = {
                'stats': processed_stats
            }

    return teams


def get_historical_stats(lg, team_key, weeks):
    """Get stats for a team over multiple weeks."""
    weekly_stats = []

    for week in weeks:
        try:
            raw_matchups = lg.matchups(week=week)
            league_data = raw_matchups['fantasy_content']['league']
            scoreboard = league_data[1]['scoreboard']
            matchups_container = scoreboard['0']['matchups']

            teams = extract_all_teams_stats(matchups_container)

            if team_key in teams and teams[team_key]['stats']:
                weekly_stats.append(teams[team_key]['stats'])
            else:
                return None

        except Exception:
            return None

    return weekly_stats if weekly_stats else None


def average_stats(stats_list):
    """Average multiple stat dictionaries."""
    if not stats_list:
        return {}

    averaged = {}
    stat_keys = ['fg_pct', 'ft_pct', '3ptm', 'pts', 'reb', 'ast', 'st', 'blk', 'to']

    for stat_key in stat_keys:
        values = [s.get(stat_key, 0.0) for s in stats_list if stat_key in s]
        if values:
            averaged[stat_key] = sum(values) / len(values)
        else:
            averaged[stat_key] = 0.0

    return averaged


def compare_two_teams(team1_stats, team2_stats):
    """Compare two teams and return (team1_wins, team2_wins, category_details)."""
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

    team1_wins = 0
    team2_wins = 0
    category_details = []

    for stat_key, display_name, direction in categories:
        if stat_key not in team1_stats or stat_key not in team2_stats:
            continue

        val1 = team1_stats[stat_key]
        val2 = team2_stats[stat_key]

        # Determine winner
        if direction == 'higher':
            if val1 > val2:
                winner = 'team1'
                team1_wins += 1
            elif val2 > val1:
                winner = 'team2'
                team2_wins += 1
            else:
                winner = 'tie'
        else:  # lower is better
            if val1 < val2:
                winner = 'team1'
                team1_wins += 1
            elif val2 < val1:
                winner = 'team2'
                team2_wins += 1
            else:
                winner = 'tie'

        # Calculate percentage difference
        higher_val = max(val1, val2)
        if higher_val > 0:
            pct_diff = abs((val1 - val2) / higher_val) * 100
        else:
            pct_diff = 0

        # Competitive if within 15%
        competitive = pct_diff <= 15

        category_details.append({
            'stat': display_name,
            'team1_val': val1,
            'team2_val': val2,
            'winner': winner,
            'pct_diff': pct_diff,
            'competitive': competitive
        })

    return team1_wins, team2_wins, category_details


def predict_matchup(lg, matchup, current_week, method):
    """Predict a single matchup using specified method."""
    team1_key = matchup['team1_key']
    team2_key = matchup['team2_key']

    # Determine weeks based on method
    if method == 'last':
        weeks = [current_week - 1] if current_week > 1 else []
    elif method == 'last3':
        weeks = [w for w in range(current_week - 3, current_week) if w >= 1]
    else:  # total
        weeks = list(range(1, current_week))

    if not weeks:
        return {'available': False}

    # Get historical stats
    team1_history = get_historical_stats(lg, team1_key, weeks)
    team2_history = get_historical_stats(lg, team2_key, weeks)

    if not team1_history or not team2_history:
        return {'available': False, 'weeks': weeks}

    # Average the stats
    team1_avg = average_stats(team1_history)
    team2_avg = average_stats(team2_history)

    # Compare teams
    team1_wins, team2_wins, category_details = compare_two_teams(team1_avg, team2_avg)

    return {
        'available': True,
        'team1_wins': team1_wins,
        'team2_wins': team2_wins,
        'category_details': category_details,
        'weeks_used': len(weeks)
    }


def display_predictions(matchups, predictions, week, method):
    """Display predicted matchup results."""
    # ANSI color codes
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    method_names = {
        'last': 'Based on Last Week',
        'last3': 'Based on Last 3 Weeks Average',
        'total': 'Based on Season Average'
    }

    print(f"\n{BOLD}{'═' * 100}{RESET}")
    print(f"{BOLD}WEEK {week} MATCHUP PREDICTIONS - {method_names[method]}{RESET}")
    print(f"{BOLD}{'═' * 100}{RESET}\n")

    for i, (matchup, pred) in enumerate(zip(matchups, predictions), 1):
        team1 = matchup['team1_name'][:35]
        team2 = matchup['team2_name'][:35]

        print(f"{BOLD}MATCHUP {i}: {team1} vs {team2}{RESET}")
        print(f"{BOLD}{'─' * 100}{RESET}")

        if not pred['available']:
            print(f"{RED}No data available for this prediction.{RESET}\n")
            continue

        # Show prediction
        t1_wins = pred['team1_wins']
        t2_wins = pred['team2_wins']

        if t1_wins > t2_wins:
            print(f"Prediction: {GREEN}{team1} wins {t1_wins}-{t2_wins}{RESET}")
        elif t2_wins > t1_wins:
            print(f"Prediction: {GREEN}{team2} wins {t2_wins}-{t1_wins}{RESET}")
        else:
            print(f"Prediction: {YELLOW}Tie {t1_wins}-{t2_wins}{RESET}")

        print(f"(Based on {pred['weeks_used']} week(s) of data)")

        # Show competitive categories
        competitive_cats = [cat for cat in pred['category_details'] if cat['competitive']]

        if competitive_cats:
            print(f"\n{YELLOW}{BOLD}Competitive Categories (within 15%):{RESET}")
            for cat in competitive_cats:
                val1 = cat['team1_val']
                val2 = cat['team2_val']
                diff = cat['pct_diff']
                stat_name = cat['stat']

                # Format values
                if stat_name in ['FG%', 'FT%']:
                    val1_str = f"{val1:.3f}"
                    val2_str = f"{val2:.3f}"
                else:
                    val1_str = f"{val1:.1f}"
                    val2_str = f"{val2:.1f}"

                winner_indicator = ""
                if cat['winner'] == 'team1':
                    winner_indicator = f" ({BOLD}{team1} wins{RESET})"
                elif cat['winner'] == 'team2':
                    winner_indicator = f" ({BOLD}{team2} wins{RESET})"

                print(f"  {YELLOW}{stat_name:>5}: {team1[:20]} {val1_str:>6} vs {team2[:20]} {val2_str:>6} ({diff:.1f}% diff){winner_indicator}{RESET}")
        else:
            print(f"\n{BOLD}No competitive categories{RESET} (all differences > 15%)")

        print(f"\n{BOLD}{'═' * 100}{RESET}\n")


def main():
    parser = argparse.ArgumentParser(description='Predict matchup results using historical data')
    parser.add_argument('--method', type=str, required=True, choices=['last', 'last3', 'total'],
                       help='Prediction method: last=last week, last3=last 3 weeks avg, total=season avg')
    parser.add_argument('--week', type=int, default=None,
                       help='Week to predict (default: current week)')
    args = parser.parse_args()

    # Authenticate
    sc = OAuth2(None, None, from_file='oauth2.json')
    gm = yfa.Game(sc, 'nba')
    league_id = '466.l.51741'
    lg = gm.to_league(league_id)

    # Get week to predict
    if args.week is None:
        week = lg.current_week()
        print(f"Predicting current week: {week}")
    else:
        week = args.week
        print(f"Predicting Week {week} using method '{args.method}'...")

    # Get matchups for the week
    try:
        raw_matchups = lg.matchups(week=week)
    except Exception as e:
        print(f"Error fetching week {week} data: {e}")
        return

    # Navigate to matchups data
    league_data = raw_matchups['fantasy_content']['league']
    scoreboard = league_data[1]['scoreboard']
    matchups_container = scoreboard['0']['matchups']

    # Extract scheduled matchups
    matchups = extract_matchups(matchups_container)

    if not matchups:
        print(f"No matchups found for Week {week}.")
        return

    print(f"Found {len(matchups)} matchups.\n")

    # Predict each matchup
    all_predictions = []
    for matchup in matchups:
        pred = predict_matchup(lg, matchup, week, args.method)
        all_predictions.append(pred)

    # Display predictions
    display_predictions(matchups, all_predictions, week, args.method)


if __name__ == '__main__':
    main()
