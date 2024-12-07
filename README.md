# US Visa Wait Times Scraper

A Python script to scrape and analyze US visa appointment wait times from the US Department of State website.

## Features
- Scrapes visa wait times for all consulates/embassies
- Maps cities to countries
- Configurable data filtering
- CSV export with timestamps
- Multiple scraping configurations

## Installation
```bash
# Clone repository
git clone [repository-url]
cd visa-wait-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## Output
- CSV files in `output/` directory
- Three configurations:
  - Default: All data with country mapping
  - Selected columns: Specific visa types
  - No country: Raw data without country mapping

## Configuration
Modify `ScraperConfig` parameters:
```python
config = ScraperConfig(
    selected_columns=['column_names'],
    include_country=True,
    output_file='filename.csv',
    output_dir='directory'
)
```

## License
MIT

## Development Note
This project was generated using AI (Claude 3.5 Sonnet) with zero modifications - a demonstration of AI capabilities in creating complete, functional scraping tools.
Time taken: <30min
Shots: 8-10
Accuracy: 100%