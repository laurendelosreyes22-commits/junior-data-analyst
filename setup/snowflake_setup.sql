-- Run this once in the Snowflake web UI (Worksheets)
-- https://app.snowflake.com/us-east-1/cec86794/#/homepage

-- Warehouse
CREATE WAREHOUSE IF NOT EXISTS junior_data_analyst_wh
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

-- Database & schema
CREATE DATABASE IF NOT EXISTS junior_data_analyst;
CREATE SCHEMA IF NOT EXISTS junior_data_analyst.raw;

USE DATABASE junior_data_analyst;
USE SCHEMA raw;
USE WAREHOUSE junior_data_analyst_wh;

-- Raw table for Google Trends (write_pandas uses uppercase column names)
CREATE TABLE IF NOT EXISTS google_trends_raw (
  keyword        VARCHAR,
  region         VARCHAR,
  week_start     DATE,
  interest_value INTEGER,
  loaded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw table for Firecrawl metadata (full markdown lives in knowledge/raw/ files)
CREATE TABLE IF NOT EXISTS firecrawl_raw (
  source_url       VARCHAR,
  page_title       VARCHAR,
  description      VARCHAR,
  local_file_path  VARCHAR,
  scraped_at       TIMESTAMP,
  loaded_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verify
SHOW TABLES IN SCHEMA junior_data_analyst.raw;
