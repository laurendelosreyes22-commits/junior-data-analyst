import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from dashboard.rag import retrieve_context, ask_claude


def test_retrieve_context_returns_top_k():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "01-epcvip.md").write_text("EPCVIP personal loans lead generation")
        (Path(tmpdir) / "02-ppc.md").write_text("PPC advertising keywords strategy")
        (Path(tmpdir) / "03-lending.md").write_text("consumer lending market trends")
        result = retrieve_context("EPCVIP loans", tmpdir, top_k=2)
    assert result.count("Source:") == 2


def test_retrieve_context_ranks_by_keyword_overlap():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "a.md").write_text("payday loans cash advance Mississippi")
        (Path(tmpdir) / "b.md").write_text("credit cards unrelated content here")
        result = retrieve_context("payday loans cash advance", tmpdir, top_k=1)
    assert "payday loans" in result


def test_ask_claude_returns_text():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="EPCVIP is a lead gen company.")]
    with patch("dashboard.rag.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = mock_response
        result = ask_claude("What is EPCVIP?", "context text", "fake-key")
    assert result == "EPCVIP is a lead gen company."
