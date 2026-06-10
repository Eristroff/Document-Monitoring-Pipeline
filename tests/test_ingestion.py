"""Tests for the Ingestion Agent."""

from agents.ingestion import _extract_text_from_html, parse_document


def test_extract_text_from_html():
    html = "<html><body><h1>Title</h1><p>Content here.</p><script>bad()</script></body></html>"
    text = _extract_text_from_html(html)
    assert "Title" in text
    assert "Content here." in text
    assert "bad()" not in text


def test_parse_document_html():
    content = b"<html><body><p>Hello</p></body></html>"
    text = parse_document(content, "text/html")
    assert "Hello" in text


def test_parse_document_plain_text():
    content = b"Plain text document."
    text = parse_document(content, "text/plain")
    assert text == "Plain text document."
