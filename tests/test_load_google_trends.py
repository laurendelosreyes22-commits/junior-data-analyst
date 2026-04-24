import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from unittest.mock import patch
from extract.load_google_trends import extract_google_trends, KEYWORDS


def test_extract_returns_dataframe():
    mock_df = pd.DataFrame(
        {"personal loans": [85, 72, 0]},
        index=["California", "Texas", "Wyoming"]
    )
    mock_df.index.name = "geoName"

    with patch("extract.load_google_trends.TrendReq") as MockTrend:
        instance = MockTrend.return_value
        instance.interest_by_region.return_value = mock_df
        result = extract_google_trends()

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_extract_has_required_columns():
    mock_df = pd.DataFrame(
        {"personal loans": [85, 72]},
        index=["California", "Texas"]
    )
    mock_df.index.name = "geoName"

    with patch("extract.load_google_trends.TrendReq") as MockTrend:
        instance = MockTrend.return_value
        instance.interest_by_region.return_value = mock_df
        result = extract_google_trends()

    assert "KEYWORD" in result.columns
    assert "REGION" in result.columns
    assert "WEEK_START" in result.columns
    assert "INTEREST_VALUE" in result.columns


def test_all_keywords_represented():
    mock_df = pd.DataFrame(
        {"personal loans": [85]},
        index=["California"]
    )
    mock_df.index.name = "geoName"

    with patch("extract.load_google_trends.TrendReq") as MockTrend:
        instance = MockTrend.return_value
        instance.interest_by_region.return_value = mock_df
        result = extract_google_trends()

    for kw in KEYWORDS:
        assert kw in result["KEYWORD"].values
