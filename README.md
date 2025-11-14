# Fantasy Basketball Analytics

Advanced analytics toolkit for Yahoo Fantasy Basketball leagues. Automates data retrieval and provides comprehensive league-wide performance analysis beyond traditional head-to-head matchup results.

## Overview

This project reimagines fantasy basketball analytics by answering the question: **"How would my team perform against ALL teams in the league, not just my scheduled opponent?"**

Traditional fantasy basketball only shows your weekly matchup result (e.g., "you beat your opponent 6-3"). This toolkit provides a complete picture:
- How you would have performed against all 10 teams
- Your true strength independent of schedule luck
- Category-by-category league rankings
- Real-time mid-week scores and projections

Inspired by the "Possibility Matrix" Excel approach (see [info.md](info.md)), this Python implementation eliminates manual data entry and enables advanced analytics.

---

## Features

### 🎯 Current Week Analysis
- **Real-time matchup tracking** with mid-week category scores
- **Category rankings matrix** showing each team's rank (1-10) across all 9 stats
- **Strength/weakness identification** for strategic lineup and trade decisions

### 📊 League-Wide Comparisons
- View how every team performs against every other team
- Identify scheduling luck (winning/losing records that don't reflect true strength)
- Compare category competitiveness across the entire league

### 🤖 Automated Data Pipeline
- Direct integration with Yahoo Fantasy Sports API
- No manual stat copying or data entry required
- Proper handling of FG% and FT% calculations (using FGM/FGA and FTM/FTA)

### 📈 Advanced Analytics (Planned)
- Historical performance tracking across multiple weeks
- Player-level contribution analysis
- Trade impact modeling
- Playoff matchup simulations

---

## Setup

### Prerequisites
- Python 3.8+
- Yahoo Fantasy Basketball league
- Yahoo Developer App credentials

### Installation

1. **Clone the repository**
   ```bash
   cd /path/to/your/projects
   git clone <repo-url>
   cd FantasyBball
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Yahoo API credentials**

   a. Create a Yahoo Developer app:
   - Go to [Yahoo Developer Network](https://developer.yahoo.com/apps/create/)
   - Create a new app with "Fantasy Sports" API access
   - Note your **Client ID (Consumer Key)** and **Client Secret (Consumer Secret)**

   b. Configure credentials:
   ```bash
   cp oauth2.example.json oauth2.json
   # Edit oauth2.json and add your consumer_key and consumer_secret
   ```

5. **Authenticate with Yahoo**
   ```bash
   python -m src.auth
   ```
   This will open a browser for first-time OAuth authorization. Follow the prompts and paste the verification code back into the terminal.

6. **Verify setup**
   ```bash
   python -m src.quick_test
   ```
   Should display your league ID(s).

---

## Usage

### Quick Commands (Recommended)

The easiest way to run the main tools is via the Makefile:

```bash
# Show category rankings (10x9 matrix)
make rankings

# Show current matchup predictions
make matchups

# Run both rankings and matchups
make all

# First-time setup
make auth

# See all available commands
make help
```

#### Using Parameters

You can specify week numbers and output formats:

```bash
# Specific week
make matchups WEEK=5
make rankings WEEK=3

# Simple matchup view (scores only, no category breakdown)
make matchups FORMAT=simple

# Combine parameters
make matchups WEEK=4 FORMAT=simple
make all WEEK=5

# See more examples
make help
```

### Direct Python Execution

All scripts can also be run as Python modules from the project root:

```bash
# Basic usage
python -m src.<script_name>

# With parameters
python -m src.category_rankings --week 5
python -m src.show_matchups --week 3 --format simple
python -m src.show_matchups -w 4 -f detailed

# Get help for any script
python -m src.category_rankings --help
python -m src.show_matchups --help
```

### Available Tools

#### Authentication & Setup
- **`src.auth`** - OAuth authentication helper (run once to authorize)
- **`src.quick_test`** - Verify API connection and list your leagues

#### Current Week Analysis
- **`src.show_matchups`** - Display all 5 matchups with mid-week category scores
- **`src.category_rankings`** - Generate 10×9 rankings matrix showing each team's rank in all 9 stat categories

#### API Exploration (Development)
- **`src.explore_api`** - Inspect available API data structures
- **`src.api_capabilities`** - Test API method capabilities
- **`src.debug_matchups`** - Debug matchup data parsing

### Example Workflow

```bash
# Quick analysis of current week
make matchups              # See your matchup prediction (detailed)
make matchups FORMAT=simple # Quick score-only view
make rankings              # See league-wide category rankings
make all                   # Run both

# Analyze a specific week
make matchups WEEK=5       # Week 5 matchups
make rankings WEEK=5       # Week 5 rankings
make all WEEK=5            # Both for week 5

# OR use Python directly
python -m src.show_matchups
python -m src.show_matchups --week 3 --format simple
python -m src.category_rankings --week 5
```

---

## Project Structure

```
FantasyBball/
├── src/                      # Python scripts
│   ├── auth.py              # OAuth authentication
│   ├── show_matchups.py     # Current matchup display
│   ├── category_rankings.py # Category rankings matrix
│   └── ...                  # Other analysis tools
├── tests/                   # Test files
├── oauth2.json             # Your API credentials (gitignored)
├── oauth2.example.json     # Credentials template
├── requirements.txt        # Python dependencies
├── info.md                 # Detailed project documentation
├── API_FINDINGS.md         # Yahoo API research notes
└── README.md              # This file
```

---

## Documentation

- **[info.md](info.md)** - Deep dive into the "Possibility Matrix" concept, current manual Excel workflow, and improvement opportunities
- **[API_FINDINGS.md](API_FINDINGS.md)** - Yahoo Fantasy API capabilities, data structures, and query strategies
- **[Possibility Matrix.xlsm](Possibility Matrix.xlsm)** - Original Excel implementation (reference)

---

## Fantasy Basketball Categories (9-CAT)

This project analyzes standard 9-category head-to-head leagues:

| Category | Name | Direction | Type |
|----------|------|-----------|------|
| **FG%** | Field Goal % | Higher wins | Ratio |
| **FT%** | Free Throw % | Higher wins | Ratio |
| **3PTM** | 3-Pointers Made | Higher wins | Counting |
| **PTS** | Points | Higher wins | Counting |
| **REB** | Rebounds | Higher wins | Counting |
| **AST** | Assists | Higher wins | Counting |
| **ST** | Steals | Higher wins | Counting |
| **BLK** | Blocks | Higher wins | Counting |
| **TO** | Turnovers | **Lower wins** | Counting |

Each head-to-head matchup awards one point per category won (max 9-0).

---

## Development

### Running Tests
```bash
pytest -q
```

### Adding New Analysis Tools
1. Create a new script in `src/`
2. Use existing helper functions (e.g., `parse_team_stats`, `get_team_name`)
3. Follow the module execution pattern: `if __name__ == '__main__': main()`

### API Rate Limits
- Yahoo Fantasy API has rate limits
- Consider caching data locally for historical analysis
- See `API_FINDINGS.md` for recommended query strategies

---

## Roadmap

### Phase 1: Current Week Analysis ✅
- [x] OAuth authentication
- [x] Current matchup display
- [x] Category rankings matrix
- [x] Strength/weakness analysis

### Phase 2: Historical Tracking (In Progress)
- [ ] SQLite database for weekly stats storage
- [ ] Multi-week trend analysis
- [ ] Season-long performance tracking
- [ ] Automated weekly data collection

### Phase 3: Full Possibility Matrix
- [ ] Generate complete N×N matchup matrix per week
- [ ] Calculate "true record" vs. "scheduled record"
- [ ] Scheduling luck analysis
- [ ] Export to Excel (matching original format)

### Phase 4: Advanced Features
- [ ] Interactive web dashboard (Streamlit/Dash)
- [ ] Player-level contribution analysis
- [ ] Trade impact simulator
- [ ] Playoff matchup projections
- [ ] Automated weekly reports (email/Slack)

---

## Contributing

This is a personal project, but suggestions and improvements are welcome! Key areas for contribution:
- Additional analytics/visualizations
- Performance optimizations
- Database schema design for historical tracking
- Web dashboard UI/UX

---

## Security Notes

- **Never commit `oauth2.json`** - it contains your API credentials (already in `.gitignore`)
- **Regenerate credentials if exposed** - use Yahoo Developer Console
- API credentials are only for personal use with your own league data

---

## License

MIT License - see LICENSE file for details

---

## Acknowledgments

- Built on [`yahoo-fantasy-api`](https://pypi.org/project/yahoo-fantasy-api/) by spilchen
- Uses [`yahoo-oauth`](https://pypi.org/project/yahoo-oauth/) for authentication
- Inspired by years of manual Excel-based analytics frustration

---

## Support

For issues or questions:
1. Check [info.md](info.md) and [API_FINDINGS.md](API_FINDINGS.md) for detailed documentation
2. Review existing scripts in `src/` for examples
3. Examine the original Excel file ([Possibility Matrix.xlsm](Possibility Matrix.xlsm)) for context

**League ID**: `466.l.51741` (2025 NBA Season)
