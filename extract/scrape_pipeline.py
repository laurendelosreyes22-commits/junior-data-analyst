import os
import re
import time
from datetime import datetime
from pathlib import Path
import requests
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_URL = "https://api.firecrawl.dev/v2/search"

QUERIES = [
    ("EPCVIP personal loans payday loans lead generation", 5),
    ("financial services PPC advertising keywords strategy", 5),
    ("consumer lending market trends personal loans credit cards", 5),
    ("LendingTree QuinStreet MoneyMutual lead gen affiliate marketing", 3),
]

RAW_DIR = Path(__file__).parent.parent / "knowledge" / "raw"


def make_slug(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:50]


def search_query(query, limit=5):
    api_key = os.environ["FIRECRAWL_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "query": query,
        "limit": limit,
        "scrapeOptions": {"formats": ["markdown"]},
    }
    response = requests.post(FIRECRAWL_URL, headers=headers, json=payload)
    data = response.json()
    results = data.get("data", {}).get("web", [])
    return [r for r in results if r.get("markdown")]


def save_to_files(results, start_index):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, result in enumerate(results, start=start_index):
        slug = make_slug(result.get("title", f"page-{i}"))
        filename = f"{i:02d}-{slug}.md"
        filepath = RAW_DIR / filename
        content = f"Source: {result['url']}\n\n{result['markdown']}"
        filepath.write_text(content, encoding="utf-8")
        print(f"Saved: knowledge/raw/{filename}")
        saved.append({
            "SOURCE_URL": result["url"],
            "PAGE_TITLE": result.get("title", ""),
            "DESCRIPTION": result.get("description", ""),
            "LOCAL_FILE_PATH": f"knowledge/raw/{filename}",
            "SCRAPED_AT": datetime.utcnow(),
        })
    return saved


def load_to_snowflake(rows):
    df = pd.DataFrame(rows)
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )
    success, nchunks, nrows, _ = write_pandas(
        conn, df, "FIRECRAWL_RAW", quote_identifiers=False
    )
    conn.close()
    print(f"Loaded {nrows} rows to FIRECRAWL_RAW")


if __name__ == "__main__":
    all_rows = []
    file_index = 1

    for query, limit in QUERIES:
        print(f"\nSearching: {query}")
        results = search_query(query, limit=limit)
        time.sleep(2)
        rows = save_to_files(results, start_index=file_index)
        all_rows.extend(rows)
        file_index += len(rows)

    print(f"\nTotal files saved: {file_index - 1}")
    load_to_snowflake(all_rows)
