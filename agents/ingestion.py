"""Ingestion Agent — downloads, parses, and stores documents."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import pdfplumber
        import io

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        logger.exception("PDF extraction failed")
        return ""


def download_document(url: str, *, timeout: int = 30) -> tuple[bytes, str]:
    """Download a document and return (content_bytes, content_type)."""
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "DocumentMonitorBot/0.1"})
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "")


def parse_document(content: bytes, content_type: str) -> str:
    """Extract plain text from raw document bytes."""
    if "pdf" in content_type:
        return _extract_text_from_pdf(content)
    if "html" in content_type or "xml" in content_type:
        return _extract_text_from_html(content.decode("utf-8", errors="replace"))
    return content.decode("utf-8", errors="replace")


def ingest(crawl_manifest: list[dict]) -> list[dict]:
    """Process a list of crawled document metadata, download and parse each."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed: list[dict] = []

    for doc in crawl_manifest:
        url = doc.get("url", "")
        if not url:
            continue

        logger.info("Ingesting %s", url)
        try:
            content, content_type = download_document(url)
            text = parse_document(content, content_type)
        except Exception:
            logger.exception("Failed to ingest %s", url)
            continue

        record = {
            "source_name": doc.get("source_name", ""),
            "url": url,
            "title": doc.get("title", "Untitled"),
            "doc_type": doc.get("doc_type", "unknown"),
            "published_date": doc.get("published_date"),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "text": text,
            "text_length": len(text),
        }
        processed.append(record)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = PROCESSED_DIR / f"ingested_{timestamp}.json"
    serializable = [{k: v for k, v in r.items()} for r in processed]
    out_path.write_text(json.dumps(serializable, indent=2))
    logger.info("Ingestion complete: %d documents processed", len(processed))
    return processed


def ingest_from_latest_crawl() -> list[dict]:
    """Find the most recent crawl manifest and ingest its documents."""
    manifests = sorted(RAW_DIR.glob("crawl_*.json"), reverse=True)
    if not manifests:
        logger.warning("No crawl manifests found")
        return []
    with open(manifests[0]) as f:
        crawl_data = json.load(f)
    return ingest(crawl_data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = ingest_from_latest_crawl()
    print(f"Ingested {len(results)} documents.")
