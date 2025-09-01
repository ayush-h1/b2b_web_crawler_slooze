Slooze Take-Home Challenge — Data Engineering (B2B Crawler + EDA)

Overview
This project implements a complete data pipeline for crawling and analyzing B2B marketplace listings from IndiaMART and Alibaba. It includes an asynchronous Python crawler (built with httpx, parsel, selectolax, and tenacity) configurable via YAML, with product data modeled using pydantic, progress tracked via tqdm, and a Typer-powered CLI for streamlined usage. The pipeline supports fetching raw JSONL data, cleaning and deduplicating into structured CSVs using pandas and numpy, and generating exploratory data analysis reports with matplotlib visualizations. Outputs include product categories, price distributions, supplier regions, and data quality gaps. All datasets are stored under `data/` and charts under `artifacts/eda/`. The solution is modular, reproducible, and easily extensible for further insights or deployment.

Tech Stack
- **Python 3.11+** — core language  
- **httpx (async)** — HTTP client for crawling  
- **parsel + selectolax** — HTML parsing and CSS selectors  
- **pydantic** — structured product models and validation  
- **tqdm** — progress bars  
- **typer** — CLI framework  
- **tenacity** — retry logic for failed requests  
- **pandas + numpy** — data cleaning and transformation  
- **matplotlib** — visualization for EDA  
- **PyYAML** — configuration management  

Quickstart

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate   # on Linux/Mac
   .venv\Scripts\activate                               # on Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run a crawl (collect raw data from IndiaMART & Alibaba):

bash
Copy code
python -m src.cli crawl --site both --max-pages 2 --out data/raw/products.jsonl
Clean and deduplicate the data into CSV:

bash
Copy code
python -m src.cli clean --inp data/raw/products.jsonl --out data/clean/products.csv
Run exploratory data analysis (EDA) with charts:

bash
Copy code
python -m src.cli eda --inp data/clean/products.csv
Project Workflow
Data Collection → Crawl IndiaMART & Alibaba product listings (JSONL format).

Data Cleaning → Deduplicate, normalize, and export to CSV.

EDA → Generate summary statistics and visualizations:

Price distributions (price_lo_hist.png)

Top categories (top_categories.png)

Supplier regions (top_regions.png)

Artifacts are written to artifacts/eda/ and summary CSVs to data/eda/.

Repository Structure
bash
Copy code
slooze_b2b_crawler/
├── configs/                # YAML configs (categories, settings)
├── data/
│   ├── raw/                # Raw JSONL crawled data
│   ├── clean/              # Cleaned CSV data
│   └── eda/                # EDA summary CSVs
├── artifacts/eda/          # Visualization charts
├── src/                    # Source code (crawler, ETL, EDA)
│   ├── cli.py              # CLI entrypoint
│   ├── sites/              # Site-specific crawlers
│   ├── pipelines/          # Data pipelines (JSONL writer, etc.)
│   ├── common/             # Shared utils, models
│   └── eda/                # EDA report generator
├── requirements.txt        # Dependencies
└── README.md               # Documentation
