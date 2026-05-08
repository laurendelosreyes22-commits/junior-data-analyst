import os
import time
from datetime import datetime
import pandas as pd
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

KEYWORDS = [
    "personal loans",
    "payday loans",
    "credit cards",
    "installment loans",
    "cash advance",
]


def fetch_keyword(pytrends, keyword, max_retries=3):
    for attempt in range(max_retries):
        try:
            pytrends.build_payload([keyword], timeframe="today 12-m", geo="US")
            df = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True)
            return df
        except TooManyRequestsError:
            wait = 120 * (attempt + 1)  # 120s, 240s, 360s
            print(f"Rate limited on '{keyword}' (attempt {attempt + 1}). Waiting {wait}s...")
            time.sleep(wait)
    print(f"WARNING: Failed to fetch '{keyword}' after {max_retries} retries — skipping.")
    return None


def extract_google_trends():
    pytrends = TrendReq(hl="en-US", tz=360)
    rows = []

    for i, keyword in enumerate(KEYWORDS):
        if i > 0:
            time.sleep(10)  # pause between keywords to avoid rate limits
        df = fetch_keyword(pytrends, keyword)
        if df is None:
            continue  # skip this keyword, keep going with the rest
        df.index.name = "geoName"
        df = df.reset_index()

        value_col = [c for c in df.columns if c != "geoName"][0]
        for _, row in df.iterrows():
            rows.append({
                "KEYWORD": keyword,
                "REGION": row["geoName"],
                "WEEK_START": datetime.today().date(),
                "INTEREST_VALUE": int(row[value_col]) if pd.notna(row[value_col]) else 0,
            })

    return pd.DataFrame(rows)


def load_to_snowflake(df):
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
        conn, df, "GOOGLE_TRENDS_RAW", quote_identifiers=False
    )
    conn.close()
    print(f"Loaded {nrows} rows to GOOGLE_TRENDS_RAW")


if __name__ == "__main__":
    df = extract_google_trends()
    print(f"Extracted {len(df)} rows")
    load_to_snowflake(df)
