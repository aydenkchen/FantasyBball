.PHONY: help rankings matchups auth test all

# Default target - show help
help:
	@echo "Fantasy Basketball Analytics - Quick Commands"
	@echo ""
	@echo "Usage: make <command>"
	@echo ""
	@echo "Available commands:"
	@echo "  make rankings      - Show category rankings matrix (10x9 grid)"
	@echo "  make matchups      - Show current week's matchup predictions"
	@echo "  make all           - Run both rankings and matchups"
	@echo "  make auth          - Authenticate with Yahoo API"
	@echo "  make test          - Run quick API connection test"
	@echo ""
	@echo "Other useful scripts:"
	@echo "  make explore       - Explore API capabilities"
	@echo "  make debug         - Debug matchup data"

# Main analysis tools
rankings:
	@echo "Fetching category rankings..."
	@python -m src.category_rankings

matchups:
	@echo "Fetching current matchup predictions..."
	@python -m src.show_matchups

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
