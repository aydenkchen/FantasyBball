# Yahoo Fantasy API - Key Findings

## Summary

The `lg.matchups(week=N)` method provides **everything needed** to automate the Possibility Matrix! No more manual data entry or percentage calculations.

---

## ✅ Answers to Key Questions

### 1. Does `matchups()` include weekly stats?

**YES!** Each matchup contains complete team stats with `"coverage_type": "week"`.

### 2. Are FGM/FGA and FTM/FTA available separately?

**YES!** Critical discovery:
- **stat_id "9004003"**: FGM/FGA as string "176/371"
- **stat_id "9007006"**: FTM/FTA as string "79/106"

This solves the manual FG%/FT% calculation problem!

### 3. Can we get mid-week stats?

**YES!** Status shows `"midevent"` when week is in progress, with real-time stat updates.

### 4. Is this weekly or cumulative data?

**NEEDS TESTING** - The data shows `"coverage_type": "week"` but we need to verify if it's:
- Weekly performance only (what we need)
- OR season-to-date cumulative (would require delta calculation)

---

## Data Structure from `lg.matchups(week=1)`

```json
{
  "matchup": {
    "week": "1",
    "status": "midevent",  // or "postevent" when complete
    "stat_winners": [
      {"stat_winner": {"stat_id": "5", "winner_team_key": "466.l.51741.t.6"}}
    ],
    "teams": {
      "0": {
        "team": [
          { "team_key": "466.l.51741.t.1", "name": "Edey is the new Jokić" },
          {
            "team_stats": {
              "coverage_type": "week",
              "week": "1",
              "stats": [
                {"stat": {"stat_id": "9004003", "value": "176/371"}},  // FGM/FGA
                {"stat": {"stat_id": "5", "value": ".474"}},          // FG%
                {"stat": {"stat_id": "9007006", "value": "79/106"}},  // FTM/FTA
                {"stat": {"stat_id": "8", "value": ".745"}},          // FT%
                {"stat": {"stat_id": "10", "value": "53"}},           // 3PTM
                {"stat": {"stat_id": "12", "value": "484"}},          // PTS
                {"stat": {"stat_id": "15", "value": "171"}},          // REB
                {"stat": {"stat_id": "16", "value": "103"}},          // AST
                {"stat": {"stat_id": "17", "value": "38"}},           // ST
                {"stat": {"stat_id": "18", "value": "19"}},           // BLK
                {"stat": {"stat_id": "19", "value": "68"}}            // TO
              ]
            },
            "team_points": {"total": "7"},  // Categories won in actual matchup
            "team_remaining_games": {
              "total": {
                "remaining_games": 7,
                "live_games": 0,
                "completed_games": 29
              }
            }
          }
        ]
      }
    }
  }
}
```

---

## Stat ID Reference

| Stat | Display Name | Stat ID | Format | Example |
|------|--------------|---------|--------|---------|
| FGM/FGA | - | 9004003 | "made/attempted" | "176/371" |
| FG% | FG% | 5 | Decimal string | ".474" |
| FTM/FTA | - | 9007006 | "made/attempted" | "79/106" |
| FT% | FT% | 8 | Decimal string | ".745" |
| 3PTM | 3PTM | 10 | Integer string | "53" |
| PTS | PTS | 12 | Integer string | "484" |
| REB | REB | 15 | Integer string | "171" |
| AST | AST | 16 | Integer string | "103" |
| ST | ST | 17 | Integer string | "38" |
| BLK | BLK | 18 | Integer string | "19" |
| TO | TO | 19 | Integer string | "68" |

---

## Recommended Data Query Strategy

### Option 1: Query by Week (Recommended)
```python
# Fetch all matchups for a specific week
matchups = lg.matchups(week=1)

# Pros:
# - One API call gets all teams' stats for the week
# - Already organized by matchup structure
# - Includes stat winners and metadata

# Cons:
# - May need to verify if stats are weekly or cumulative
```

### Option 2: Query by Team
```python
# Fetch each team individually
teams = lg.teams()
for team_key in teams:
    team = lg.to_team(team_key)
    # Team object has limited stat methods - matchups() is better
```

**Verdict**: Use `lg.matchups(week=N)` - it's purpose-built for this use case!

---

## Data Storage Strategy

### Recommended Approach

**Don't call API repeatedly** - Store data locally after fetching:

1. **Weekly batch job**: Run once after week ends (status = "postevent")
2. **Store in SQLite database**: Fast queries, historical analysis
3. **Cache raw API responses**: Useful for debugging/reprocessing

### Database Schema (Proposed)

```sql
-- Store weekly stats for each team
CREATE TABLE weekly_stats (
    id INTEGER PRIMARY KEY,
    team_key TEXT,
    week INTEGER,
    season INTEGER,
    fgm INTEGER,
    fga INTEGER,
    fg_pct REAL,
    ftm INTEGER,
    fta INTEGER,
    ft_pct REAL,
    threes INTEGER,
    points INTEGER,
    rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_key, week, season)
);

-- Store possibility matrix results
CREATE TABLE matchup_results (
    id INTEGER PRIMARY KEY,
    week INTEGER,
    season INTEGER,
    team1_key TEXT,
    team2_key TEXT,
    team1_wins INTEGER,  -- Categories won by team1
    team2_wins INTEGER,  -- Categories won by team2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week, season, team1_key, team2_key)
);

-- Store team metadata
CREATE TABLE teams (
    team_key TEXT PRIMARY KEY,
    team_id INTEGER,
    name TEXT,
    season INTEGER
);
```

---

## Next Steps to Verify

1. **Test if stats are weekly or cumulative**:
   ```python
   week1 = lg.matchups(week=1)
   week2 = lg.matchups(week=2)
   # Compare if week2 values = week1 + delta OR just delta
   ```

2. **Test completed vs in-progress weeks**:
   - Do stats change during the week?
   - When does status flip from "midevent" to "postevent"?

3. **Verify FGM/FGA parsing**:
   ```python
   fgm_fga = "176/371"
   fgm, fga = map(int, fgm_fga.split('/'))
   calculated_pct = fgm / fga  # Should match provided FG%
   ```

---

## Implementation Benefits

With this API structure, we can:

✅ **Eliminate manual data entry** - Fully automated
✅ **Calculate FG%/FT% correctly** - FGM/FGA and FTM/FTA provided
✅ **Real-time updates** - Check mid-week progress
✅ **Historical tracking** - Store all weeks in database
✅ **Generate possibility matrix** - All team stats available per week
✅ **Enhanced analytics** - Player-level data, trends, predictions
✅ **Automated reports** - Weekly summaries, scheduling luck analysis

---

## Key Discovery

**The `matchups()` method is perfect for our use case!**

It provides:
- All teams' weekly stats in one call
- FGM/FGA and FTM/FTA for accurate percentage calculations
- Matchup metadata (actual results, stat winners)
- Mid-week and final data

This means we can build a fully automated Possibility Matrix generator with no manual data entry whatsoever!
