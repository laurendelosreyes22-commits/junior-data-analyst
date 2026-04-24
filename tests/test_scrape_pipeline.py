import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from extract.scrape_pipeline import search_query, make_slug, QUERIES


def test_search_returns_results():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "web": [
                {
                    "title": "EPCVIP Loans",
                    "url": "https://epcvip.com",
                    "description": "Personal loans",
                    "markdown": "# EPCVIP"
                }
            ]
        }
    }

    with patch("extract.scrape_pipeline.requests.post", return_value=mock_response):
        results = search_query("EPCVIP personal loans", limit=1)

    assert len(results) == 1
    assert results[0]["title"] == "EPCVIP Loans"
    assert results[0]["url"] == "https://epcvip.com"
    assert results[0]["markdown"] == "# EPCVIP"


def test_search_skips_empty_markdown():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "web": [
                {"title": "Page A", "url": "https://a.com", "description": "desc", "markdown": "# Content"},
                {"title": "Page B", "url": "https://b.com", "description": "desc", "markdown": None},
            ]
        }
    }

    with patch("extract.scrape_pipeline.requests.post", return_value=mock_response):
        results = search_query("test query", limit=2)

    assert len(results) == 1
    assert results[0]["title"] == "Page A"


def test_make_slug_converts_title():
    assert make_slug("EPCVIP Personal Loans!") == "epcvip-personal-loans"
    assert make_slug("LendingTree & QuinStreet") == "lendingtree-quinstreet"
