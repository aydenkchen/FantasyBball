.PHONY: help rankings matchups possibility predict auth test all

# Week parameter (can be overridden: make matchups WEEK=5)
WEEK ?=

# Format parameter for matchups (simple or detailed)
FORMAT ?= detailed

# Method parameter for predictions (last, last3, total)
METHOD ?= last

# Range parameter for category rankings (last3, total)
RANGE ?=

# Default target - show help
help:
	@echo "Fantasy Basketball Analytics - Quick Commands"
	@echo ""
	@echo "Usage: make <command> [WEEK=N] [FORMAT=simple|detailed]"
	@echo ""
	@echo "Available commands:"
	@echo "  make rankings      - Show category rankings matrix (10x9 grid)"
	@echo "  make matchups      - Show current week's matchup predictions"
	@echo "  make possibility   - Show full NxN possibility matrix (all vs all)"
	@echo "  make predict       - Predict matchups using historical data"
	@echo "  make all           - Run rankings, matchups, and possibility matrix"
	@echo "  make auth          - Authenticate with Yahoo API"
	@echo "  make test          - Run quick API connection test"
	@echo ""
	@echo "Parameters:"
	@echo "  WEEK=N            - Specify week number (default: current week)"
	@echo "  FORMAT=simple     - Simple matchup view (scores only)"
	@echo "  FORMAT=detailed   - Detailed matchup view with categories (default)"
	@echo "  METHOD=last       - Predict using last week (default)"
	@echo "  METHOD=last3      - Predict using last 3 weeks average"
	@echo "  METHOD=total      - Predict using season total average"
	@echo "  RANGE=last3       - Rankings: last 3 weeks average"
	@echo "  RANGE=total       - Rankings: season total average"
	@echo ""
	@echo "Examples:"
	@echo "  make matchups                        - Current week, detailed"
	@echo "  make matchups WEEK=5                 - Week 5, detailed"
	@echo "  make matchups FORMAT=simple          - Current week, simple view"
	@echo "  make rankings WEEK=5                 - Week 5 rankings"
	@echo "  make rankings RANGE=last3            - Last 3 weeks average rankings"
	@echo "  make rankings WEEK=8 RANGE=last3     - Weeks 6-8 average rankings"
	@echo "  make rankings RANGE=total            - Season total average rankings"
	@echo "  make possibility WEEK=4              - Week 4 possibility matrix"
	@echo "  make predict WEEK=5 METHOD=last3     - Predict week 5 using last 3 weeks"
	@echo "  make all WEEK=4                      - All tools for week 4"
	@echo ""
	@echo "Other useful scripts:"
	@echo "  make explore       - Explore API capabilities"
	@echo "  make debug         - Debug matchup data"

# Main analysis tools
rankings:
	@echo "Fetching category rankings..."
	@python -m src.category_rankings $(if $(WEEK),--week $(WEEK)) $(if $(RANGE),--range $(RANGE))

matchups:
	@echo "Fetching matchup predictions..."
	@python -m src.show_matchups $(if $(WEEK),--week $(WEEK)) --format $(FORMAT)

possibility:
	@echo "Generating possibility matrix..."
	@python -m src.possibility_matrix $(if $(WEEK),--week $(WEEK))

predict:
	@echo "Predicting matchups..."
	@python -m src.predict_matchups --method $(METHOD) $(if $(WEEK),--week $(WEEK))

all: matchups rankings possibility
	@echo ""
	@echo "Analysis complete!"

# Setup and testing
auth:
	@python -m src.auth

test:
	@python -m src.quick_test

# Development tools
explore:
	@python -m src.explore_api

debug:
	@python -m src.debug_matchups

current:
	@python -m src.current_matchups

league:
	@python -m src.league_data
