"""Orchestrator Agent — schedules and coordinates the pipeline agents."""

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

SCHEDULE_PATH = Path(__file__).resolve().parent.parent / "config" / "schedule.yaml"


def load_schedule() -> dict:
    with open(SCHEDULE_PATH) as f:
        return yaml.safe_load(f)


def run_pipeline() -> None:
    """Execute the full pipeline: crawl -> ingest -> analyze -> report."""
    from agents.crawler import crawl
    from agents.ingestion import ingest
    from agents.analysis import analyze_batch
    from agents.reporting import generate_report

    logger.info("Pipeline started at %s", datetime.now(timezone.utc).isoformat())

    logger.info("Step 1/4: Crawling sources...")
    new_docs = crawl()
    if not new_docs:
        logger.info("No new documents found. Pipeline complete.")
        return

    logger.info("Step 2/4: Ingesting %d documents...", len(new_docs))
    ingested = ingest(new_docs)

    logger.info("Step 3/4: Analyzing %d documents...", len(ingested))
    analyses = analyze_batch(ingested)

    logger.info("Step 4/4: Generating report...")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    generate_report(analyses, start_date="(auto)", end_date=today)

    logger.info("Pipeline complete. %d documents processed.", len(analyses))


def run_scheduled() -> None:
    """Start the APScheduler-based scheduled execution."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    config = load_schedule()
    tz = config.get("settings", {}).get("timezone", "UTC")

    scheduler = BlockingScheduler(timezone=tz)

    cron_expr = config["pipeline"]["reporting"]["cron"]
    parts = cron_expr.split()
    scheduler.add_job(
        run_pipeline,
        CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
            timezone=tz,
        ),
        id="weekly_pipeline",
        name="Weekly Document Pipeline",
    )

    logger.info("Scheduler started. Next run based on cron: %s", cron_expr)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Document Monitoring Pipeline Orchestrator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-now", action="store_true", help="Run the full pipeline immediately")
    group.add_argument("--schedule", action="store_true", help="Start the scheduler")
    args = parser.parse_args()

    if args.run_now:
        run_pipeline()
    elif args.schedule:
        run_scheduled()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    main()
