import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict

CATEGORY_KEYWORDS = {
    "工業設計": "工業設計",
    "介面設計": "介面設計",
    "體驗設計": "體驗設計",
    "平面設計": "平面設計",
    "品牌設計": "品牌設計",
}

# keywords to exclude when searching for UX design without UI elements
EXCLUDE_FOR_UX = ["UI", "介面"]

API_URL = "https://www.104.com.tw/jobs/search/list"


def fetch_jobs(keyword, page=1):
    params = {
        "ro": 0,
        "kwop": 7,
        "keyword": keyword,
        "order": 11,
        "asc": 0,
        "page": page,
        "mode": "s",
    }
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def crawl_category(keyword):
    month_counts = defaultdict(int)
    page = 1
    one_year_ago = datetime.today() - timedelta(days=365)
    while True:
        data = fetch_jobs(keyword, page)
        if data.get("error") or not data.get("data", {}).get("list"):
            break
        for item in data["data"]["list"]:
            appear_date = item.get("appearDate")
            if not appear_date:
                continue
            date_obj = datetime.strptime(appear_date, "%Y/%m/%d")
            if date_obj < one_year_ago:
                # Stop if older than one year
                return month_counts
            month_key = date_obj.strftime("%Y-%m")
            month_counts[month_key] += 1
        page += 1
    return month_counts


def crawl_ux_without_ui():
    month_counts = defaultdict(int)
    page = 1
    one_year_ago = datetime.today() - timedelta(days=365)
    while True:
        data = fetch_jobs("體驗設計", page)
        if data.get("error") or not data.get("data", {}).get("list"):
            break
        for item in data["data"]["list"]:
            appear_date = item.get("appearDate")
            if not appear_date:
                continue
            date_obj = datetime.strptime(appear_date, "%Y/%m/%d")
            if date_obj < one_year_ago:
                return month_counts
            job_name = item.get("jobName", "")
            if any(ex in job_name for ex in EXCLUDE_FOR_UX):
                continue
            month_key = date_obj.strftime("%Y-%m")
            month_counts[month_key] += 1
        page += 1
    return month_counts


def merge_months(*dicts):
    all_months = sorted({k for d in dicts for k in d.keys()})
    return all_months


def main():
    results = {}
    for cat, kw in CATEGORY_KEYWORDS.items():
        if cat == "體驗設計":
            counts = crawl_ux_without_ui()
        else:
            counts = crawl_category(kw)
        results[cat] = counts

    months = merge_months(*results.values())
    months.sort()
    plt.figure(figsize=(10, 6))
    for cat, counts in results.items():
        y = [counts.get(m, 0) for m in months]
        plt.plot(months, y, marker="o", label=cat)
    plt.xlabel("Month")
    plt.ylabel("Job Count")
    plt.title("104 Design Jobs in the Past Year")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("104_jobs_plot.png")
    plt.show()


if __name__ == "__main__":
    main()
