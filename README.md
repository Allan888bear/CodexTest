# CodexTest

This repository contains example Python scripts.

## 104 Job Crawler

The `scripts/104_job_spider.py` script queries Taiwan's 104 job website and
counts the number of design-related job postings per month for the last year.
The categories tracked are industrial design, interface design, UX design
(excluding UI related positions), graphic design, and brand design. The script
outputs a line chart `104_jobs_plot.png` that visualizes the job counts.

### Requirements

- Python 3
- `requests`
- `beautifulsoup4`
- `matplotlib`

Install dependencies using pip:

```bash
pip install requests beautifulsoup4 matplotlib
```

### Usage

Run the crawler from the repository root:

```bash
python scripts/104_job_spider.py
```

The script requires internet access to fetch data from 104.com.tw.
