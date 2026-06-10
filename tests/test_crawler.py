"""Tests for the Crawler Agent."""

import json
from unittest.mock import MagicMock, patch

from agents.crawler import _content_hash, _parse_json_listing, load_sources


def test_content_hash_deterministic():
    data = b"hello world"
    assert _content_hash(data) == _content_hash(data)


def test_content_hash_differs_for_different_input():
    assert _content_hash(b"a") != _content_hash(b"b")


def test_parse_json_listing_extracts_results():
    source = {"name": "Test", "doc_type": "regulation"}
    data = {
        "results": [
            {"html_url": "https://example.com/doc1", "title": "Doc 1", "publication_date": "2025-01-01"},
            {"html_url": "https://example.com/doc2", "title": "Doc 2", "publication_date": "2025-01-02"},
        ]
    }
    docs = _parse_json_listing(data, source)
    assert len(docs) == 2
    assert docs[0]["title"] == "Doc 1"
    assert docs[0]["source_name"] == "Test"
    assert docs[1]["url"] == "https://example.com/doc2"


def test_load_sources_returns_list():
    sources = load_sources()
    assert isinstance(sources, list)
    assert len(sources) > 0
    assert "name" in sources[0]
