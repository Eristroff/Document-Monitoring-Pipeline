"""Analysis Agent — summarizes documents, extracts entities, and detects changes."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import anthropic

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "analysis_prompt.txt"

MAX_TEXT_CHARS = 80_000


def _load_prompt_template() -> str:
    return PROMPT_PATH.read_text()


def analyze_document(doc: dict, *, client: anthropic.Anthropic | None = None) -> dict:
    """Send a single document to the LLM for structured analysis."""
    if client is None:
        client = anthropic.Anthropic()

    template = _load_prompt_template()
    prompt = template.format(
        title=doc.get("title", "Untitled"),
        source=doc.get("source_name", "Unknown"),
        date_published=doc.get("published_date", "Unknown"),
        document_text=doc.get("text", "")[:MAX_TEXT_CHARS],
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    try:
        analysis = json.loads(response_text)
    except json.JSONDecodeError:
        analysis = {"raw_response": response_text}

    return {
        "url": doc.get("url", ""),
        "title": doc.get("title", "Untitled"),
        "source_name": doc.get("source_name", ""),
        "doc_type": doc.get("doc_type", ""),
        "published_date": doc.get("published_date"),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "analysis": analysis,
    }


def analyze_batch(documents: list[dict]) -> list[dict]:
    """Analyze a batch of ingested documents."""
    client = anthropic.Anthropic()
    results: list[dict] = []

    for doc in documents:
        logger.info("Analyzing: %s", doc.get("title", doc.get("url", "")))
        try:
            result = analyze_document(doc, client=client)
            results.append(result)
        except Exception:
            logger.exception("Analysis failed for %s", doc.get("url", ""))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = PROCESSED_DIR / f"analysis_{timestamp}.json"
    out_path.write_text(json.dumps(results, indent=2))
    logger.info("Analysis complete: %d documents analyzed", len(results))
    return results


def analyze_from_latest_ingestion() -> list[dict]:
    """Find the most recent ingestion output and analyze it."""
    files = sorted(PROCESSED_DIR.glob("ingested_*.json"), reverse=True)
    if not files:
        logger.warning("No ingestion files found")
        return []
    with open(files[0]) as f:
        docs = json.load(f)
    return analyze_batch(docs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = analyze_from_latest_ingestion()
    print(f"Analyzed {len(results)} documents.")
