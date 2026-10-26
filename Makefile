# Carpinteria Salt Marsh Fish Observatory
# Makefile for R-based data pipeline

.PHONY: all clean data analysis json report verify serve help

# Default target
all: report verify
	@echo "Build complete! Run 'make serve' to view the observatory."

# Help
help:
	@echo "Carpinteria Salt Marsh Fish Observatory - Build Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all       - Validate sources, rebuild analysis/guide/views, verify outputs"
	@echo "  data      - Validate current revision-9 files in the shared cache"
	@echo "  analysis  - Run statistical analyses in R"
	@echo "  json      - Export analysis results to JSON for D3"
	@echo "  serve     - Start local HTTP server (http://localhost:8000)"
	@echo "  clean     - Remove generated outputs"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Quick start:"
	@echo "  make all       # Run full pipeline"
	@echo "  make serve     # View the observatory"

# Download data from EDI repository
data:
	@echo "Validating revision-9 files in the shared SONGS cache..."
	Rscript R/01_download_data.R

# Run statistical analyses
analysis: data
	@echo "Running statistical analyses..."
	Rscript R/02_analysis.R
	@echo "Analysis complete."

# Export to JSON for D3 dashboard
json: analysis
	@echo "Exporting JSON for D3 dashboard..."
	Rscript R/03_export_json.R
	@echo "Running advanced analyses..."
	Rscript R/04_advanced_analysis.R
	Rscript R/05_export_advanced_json.R
	python3 scripts/update_public_views.py
	@echo "JSON export complete: outputs/dashboard_data.json"

report: json
	Rscript -e 'rmarkdown::render("carpinteria_salt_marsh_fishes.Rmd", quiet=TRUE)'

verify:
	python3 scripts/verify_refresh.py
	node scripts/verify_site_scripts.cjs

# Start local HTTP server for static site
serve:
	@echo "Starting Carpinteria Salt Marsh Fish Observatory..."
	@echo "Visit: http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	python3 -m http.server 8000

# Clean generated files
clean:
	@echo "Cleaning generated outputs..."
	rm -f outputs/dashboard_data.json
	rm -f outputs/analysis_results.rds
	@echo "Clean complete."

# Deep clean - also remove downloaded data
clean-all:
	@echo "Raw data are immutable; clean-all is disabled."
