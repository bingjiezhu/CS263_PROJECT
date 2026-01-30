"""Unit tests for parsing helper functions."""

from llm.parsing import extract_choice, extract_label


def test_extract_choice_basic():
    """Basic answer patterns should be captured."""
    text = "Final: B"
    assert extract_choice(text, ["x", "y", "z"]) == "B"


def test_extract_label_basic():
    """Label extraction should match the label set."""
    text = "positive"
    assert extract_label(text, ["positive", "negative"]) == "positive"
