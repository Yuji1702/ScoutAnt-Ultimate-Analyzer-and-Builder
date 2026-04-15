# Module Documentation: events_scraper
The `events_scraper` is the data acquisition layer.

## Components
- **Stats_from_events_page.py**: The primary scraper for event-based data.
- **analyzer.py**: Cleans and structures raw scraped data for the ML pipeline.
- **repair_db.py**: Utility to fix inconsistencies in the database.

## Workflow
Scraping $\rightarrow$ Raw JSON/CSV $\rightarrow$ `analyzer.py` $\rightarrow$ `ml_pipeline/data` (Parquet)
