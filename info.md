# Possibility Matrix - Fantasy Basketball Analytics

## Main Goal

The **Possibility Matrix** is designed to provide a **complete league-wide strength comparison** for fantasy basketball teams. Unlike traditional fantasy basketball which only shows how your team performed against your scheduled opponent each week, the Possibility Matrix calculates how **every team would have performed against every other team** in the league for that week.

This reveals:
- **True team strength** independent of schedule
- **Scheduling luck** (teams may have winning records despite being weak, or losing records despite being strong)
- **Category-specific advantages** against all opponents
- **Strategic insights** for trades, waiver pickups, and lineup decisions

Instead of just knowing "I beat my opponent 6-3 this week," you can see "I would have beaten 8 out of 10 teams this week" - providing a much clearer picture of your team's actual performance and league standing.

---

## Current Excel Implementation

### File Structure

**File**: `Possibility Matrix.xlsm`
- **15 weekly sheets**: Week 1, Week 2, ..., Week 17 (Week 13 skipped for NBA All-Star break)
- **10 teams** in the league
- **9 categories**: FG%, FT%, 3PTM, PTS, REB, AST, ST, BLK, TO

### Sheet Layout (Each Week)

Each weekly sheet has 4 main sections:

#### 1. Last Week (Columns B-K)
- Stores previous week's **season-to-date cumulative totals**
- Used as baseline for calculating weekly changes
- Week 1 starts at all zeros

#### 2. Import (Columns M-V)
- Current week's **season-to-date cumulative statistics**
- **Manual data entry point** - stats copied from Yahoo Fantasy website
- FG% and FT% stored as formulas: `=makes/attempts`

#### 3. Calculation (Columns X-AG)
- Calculates **weekly delta**: Current week cumulative - Last week cumulative
- Formula pattern: `=[Import Cell] - [Last Week Cell]`
- Example: `=P3-E3` (this week's 3PTM minus last week's 3PTM)
- Isolates single-week performance for fair matchup comparisons

#### 4. Possibility Matrix (Columns AI-AS)
- **10×10 grid** showing head-to-head results for all possible matchups
- Format: "X-Y" where X = categories won, Y = categories lost
- Example: "7-2" means team won 7 categories and lost 2
- Diagonal shows "-" (team vs itself)
- Symmetric inverse property: If Team A beats Team B 7-2, then Team B beats Team A 2-7

### Fantasy Categories (9-CAT)

| Category | Full Name | Direction | Type | Notes |
|----------|-----------|-----------|------|-------|
| **FG%** | Field Goal % | Higher wins | Ratio | Field goals made / attempted |
| **FT%** | Free Throw % | Higher wins | Ratio | Free throws made / attempted |
| **3PTM** | 3-Pointers Made | Higher wins | Counting | Total three-pointers made |
| **PTS** | Points | Higher wins | Counting | Total points scored |
| **REB** | Rebounds | Higher wins | Counting | Total rebounds |
| **AST** | Assists | Higher wins | Counting | Total assists |
| **ST** | Steals | Higher wins | Counting | Total steals |
| **BLK** | Blocks | Higher wins | Counting | Total blocks |
| **TO** | Turnovers | **Lower wins** | Counting | Total turnovers (only negative stat) |

### Matchup Scoring Rules

- Teams compete across all 9 categories
- Winner of each category gets 1 point
- Loser gets 0 points
- Ties = 0.5 points each
- Maximum possible score: 9-0

---

## Current Manual Process & Pain Points

### Weekly Workflow

1. **Navigate to Yahoo Fantasy website** after the week ends
2. **Copy season-to-date cumulative stats** for all 10 teams
3. **Paste into "Import" section** of the current week's sheet
4. **Manually calculate and enter FG% and FT%**:
   - Problem: FG% and FT% are **not cumulative via simple subtraction** (this week - last week)
   - Percentages require makes/attempts tracking: `(current_makes - last_makes) / (current_attempts - last_attempts)`
   - Current solution: Manually calculate and type in by hand each week
5. **Calculate or run macro** to generate the Possibility Matrix
6. **Copy current week's "Import"** to next week's "Last Week" section

### Major Pain Points

1. **Manual data entry** - Copy/paste from website is tedious and error-prone
2. **FG% and FT% calculation** - Cannot use simple delta formula, requires manual calculation
3. **Repetitive process** - Same workflow every week for entire season (17 weeks)
4. **No validation** - Easy to paste wrong data or miss a team
5. **Limited analysis** - Excel doesn't easily support advanced visualizations or trend analysis
6. **VBA dependency** - Macros may break, not portable, hard to modify

---

## Data Flow Between Weeks

```
Week 1:
  Last Week: All 0s (season start)
  Import: Week 1 cumulative stats (manually entered)
  Calculation: Week 1 - 0 = Week 1 performance
  Matrix: All possible Week 1 matchups

Week 2:
  Last Week: Week 1's Import section (copied forward)
  Import: Week 2 cumulative stats (manually entered)
  Calculation: Week 2 cumulative - Week 1 cumulative = Week 2 increment
  Matrix: All possible Week 2 matchups

Week N:
  Last Week: Week (N-1) cumulative
  Import: Week N cumulative (manually entered from Yahoo)
  Calculation: Week N - Week (N-1) = Weekly performance
  Matrix: All possible Week N matchups
```

**Critical Detail**: The "Import" section always contains **season-to-date cumulative totals**, not weekly stats. Weekly performance is derived by subtracting the previous week's cumulative totals.

---

## Potential Improvements with Yahoo Fantasy API

### Automated Data Collection

Instead of manually copying stats from the website:
- **Fetch cumulative stats** directly via Yahoo Fantasy API
- **Store in database** for historical tracking
- **Automatically calculate weekly deltas** including proper FG% and FT% handling

### Proper Percentage Calculations

The API can provide:
- `FGM` (Field Goals Made) and `FGA` (Field Goals Attempted)
- `FTM` (Free Throws Made) and `FTA` (Free Throws Attempted)

This allows accurate weekly percentage calculation:
```python
weekly_fg_pct = (current_fgm - last_fgm) / (current_fga - last_fga)
weekly_ft_pct = (current_ftm - last_ftm) / (current_fta - last_fta)
```

### Enhanced Analytics

With programmatic access to data:
- **Historical trends** - Track team performance over time
- **Player-level analysis** - See which players drive category wins/losses
- **Predictive modeling** - Forecast future matchups
- **Interactive dashboards** - Real-time updates, filtering, drill-downs
- **Automated reports** - Weekly summary emails or Slack notifications
- **Trade impact analysis** - Model how trades would affect future matchups

### Database Schema

Proposed structure for tracking all data:
```
teams: id, name, league_id
weeks: id, week_number, season, start_date, end_date
weekly_stats: team_id, week_id, fg_pct, ft_pct, 3ptm, pts, reb, ast, st, blk, to
  (stores weekly performance, not cumulative)
matchup_results: week_id, team1_id, team2_id, team1_wins, team2_wins
  (stores all N×N matchup results per week)
```

---

## League Information

**League ID**: `466.l.51741`

**Teams** (10 total):
1. Edey is the new Jokić
2. Ben's Best Team
3. Zach's Amazing Team
4. Aidan's Agreeable Team
5. BK's Big Ballers
6. Ivica Zubat
7. The Real Slim Shai'dy
8. Will's Groovy Team
9. Ben's Glorious Team
10. Aden's Awe-Inspiring Team

**Season**: 2025 NBA Fantasy Basketball
**Scoring**: 9-Category Head-to-Head

---

## Next Steps (Not Yet Implemented)

Potential Python implementation could:

1. **Authenticate with Yahoo Fantasy API** (already done - see `src/auth.py`)
2. **Fetch weekly stats** for all teams automatically
3. **Calculate weekly deltas** with proper percentage handling
4. **Generate Possibility Matrix** for each week
5. **Store historical data** in SQLite database
6. **Create visualizations**:
   - Heatmaps of matchup results
   - Team strength trends over season
   - Category distribution charts
   - Scheduling luck analysis
7. **Export to Excel** (if desired) or display in interactive web dashboard
8. **Automate weekly updates** - Run script once per week, no manual entry

This would eliminate all manual data entry and provide much richer analysis capabilities.
