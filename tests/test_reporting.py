"""Tests for the Reporting Agent."""

from agents.reporting import _collect_entities, _collect_topic_counts, _count_significance


def _make_analysis(significance="high", entities=None, topics=None):
    return {
        "analysis": {
            "significance": significance,
            "entities": entities or [],
            "topics": topics or [],
        }
    }


def test_count_significance():
    analyses = [_make_analysis("high"), _make_analysis("low"), _make_analysis("high")]
    assert _count_significance(analyses, "high") == 2
    assert _count_significance(analyses, "low") == 1
    assert _count_significance(analyses, "medium") == 0


def test_collect_entities_deduplicates():
    analyses = [
        _make_analysis(entities=["EPA", "FDA"]),
        _make_analysis(entities=["EPA", "SEC"]),
    ]
    entities = _collect_entities(analyses)
    assert entities == ["EPA", "FDA", "SEC"]


def test_collect_topic_counts():
    analyses = [
        _make_analysis(topics=["regulation", "healthcare"]),
        _make_analysis(topics=["regulation", "finance"]),
    ]
    counts = _collect_topic_counts(analyses)
    assert counts["regulation"] == 2
    assert counts["healthcare"] == 1
