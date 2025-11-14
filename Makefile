.PHONY: help rankings matchups auth test all

# Week parameter (can be overridden: make matchups WEEK=5)
WEEK ?=

# Format parameter for matchups (simple or detailed)
FORMAT ?= detailed

# Default target - show help
help:
	@echo "Fantasy Basketball Analytics - Quick Commands"
	@echo ""
	@echo "Usage: make <command> [WEEK=N] [FORMAT=simple|detailed]"
	@echo ""
	@echo "Available commands:"
	@echo "  make rankings      - Show category rankings matrix (10x9 grid)"
	@echo "  make matchups      - Show current week's matchup predictions"
	@echo "  make all           - Run both rankings and matchups"
	@echo "  make auth          - Authenticate with Yahoo API"
	@echo "  make test          - Run quick API connection test"
	@echo ""
	@echo "Parameters:"
	@echo "  WEEK=N            - Specify week number (default: current week)"
	@echo "  FORMAT=simple     - Simple matchup view (scores only)"
	@echo "  FORMAT=detailed   - Detailed matchup view with categories (default)"
	@echo ""
	@echo "Examples:"
	@echo "  make matchups                    - Current week, detailed"
	@echo "  make matchups WEEK=5             - Week 5, detailed"
	@echo "  make matchups FORMAT=simple      - Current week, simple view"
	@echo "  make matchups WEEK=3 FORMAT=simple  - Week 3, simple view"
	@echo "  make rankings WEEK=5             - Week 5 rankings"
	@echo "  make all WEEK=4                  - Both tools for week 4"
	@echo ""
	@echo "Other useful scripts:"
	@echo "  make explore       - Explore API capabilities"
	@echo "  make debug         - Debug matchup data"

# Main analysis tools
rankings:
	@echo "Fetching category rankings..."
	@python -m src.category_rankings $(if $(WEEK),--week $(WEEK))

matchups:
	@echo "Fetching matchup predictions..."
	@python -m src.show_matchups $(if $(WEEK),--week $(WEEK)) --format $(FORMAT)

all: matchups rankings
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
