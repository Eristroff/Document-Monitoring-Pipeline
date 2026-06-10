"""Crawler Agent — monitors government sources and detects new/updated documents."""

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "crawler_state.db"
SOURCES_PATH = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS seen_documents (
            url TEXT PRIMARY KEY,
            content_hash TEXT,
            first_seen TEXT,
            last_checked TEXT
        )"""
    )
    conn.commit()


def load_sources() -> list[dict]:
    with open(SOURCES_PATH) as f:
        return yaml.safe_load(f)["sources"]


def _content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_source(source: dict, *, timeout: int = 30) -> list[dict]:
    """Fetch documents from a single source. Returns list of document metadata dicts."""
    url = source["url"]
    logger.info("Fetching %s (%s)", source["name"], url)
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "DocumentMonitorBot/0.1"})
        resp.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to fetch %s", source["name"])
        return []

    content_type = resp.headers.get("Content-Type", "")
    if "json" in content_type:
        return _parse_json_listing(resp.json(), source)

    return [
        {
            "source_name": source["name"],
            "url": url,
            "doc_type": source.get("doc_type", "unknown"),
            "content_hash": _content_hash(resp.content),
            "raw_bytes": resp.content,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    ]


def _parse_json_listing(data: dict, source: dict) -> list[dict]:
    results = data.get("results") or data.get("bills") or []
    docs = []
    for item in results[:20]:
        doc_url = item.get("html_url") or item.get("url") or ""
        docs.append(
            {
                "source_name": source["name"],
                "url": doc_url,
                "title": item.get("title", "Untitled"),
                "doc_type": source.get("doc_type", "unknown"),
                "published_date": item.get("publication_date") or item.get("updateDate"),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return docs


def crawl(sources: list[dict] | None = None) -> list[dict]:
    """Crawl all configured sources and return newly discovered documents."""
    if sources is None:
        sources = load_sources()

    conn = sqlite3.connect(DB_PATH)
    _init_db(conn)

    new_docs: list[dict] = []
    for source in sources:
        docs = fetch_source(source)
        for doc in docs:
            url = doc.get("url", "")
            if not url:
                continue
            row = conn.execute("SELECT content_hash FROM seen_documents WHERE url = ?", (url,)).fetchone()
            c_hash = doc.get("content_hash", "")
            now = datetime.now(timezone.utc).isoformat()
            if row is None:
                conn.execute(
                    "INSERT INTO seen_documents (url, content_hash, first_seen, last_checked) VALUES (?, ?, ?, ?)",
                    (url, c_hash, now, now),
                )
                new_docs.append(doc)
                logger.info("New document: %s", url)
            elif c_hash and row[0] != c_hash:
                conn.execute(
                    "UPDATE seen_documents SET content_hash = ?, last_checked = ? WHERE url = ?",
                    (c_hash, now, url),
                )
                doc["updated"] = True
                new_docs.append(doc)
                logger.info("Updated document: %s", url)
            else:
                conn.execute("UPDATE seen_documents SET last_checked = ? WHERE url = ?", (now, url))

    conn.commit()
    conn.close()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = RAW_DIR / f"crawl_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    serializable = [{k: v for k, v in d.items() if k != "raw_bytes"} for d in new_docs]
    manifest_path.write_text(json.dumps(serializable, indent=2))
    logger.info("Crawl complete: %d new/updated documents", len(new_docs))
    return new_docs


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = crawl()
    print(f"Discovered {len(results)} new/updated documents.")
