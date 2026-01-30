"""Unit tests for dataset adapter normalization."""

from data.adapters import adapt_example


def test_adapt_example_index_label():
    """Index labels should map to letter choices."""
    ds_cfg = {
        "name": "toy",
        "task_type": "multiple_choice",
        "question_field": "query",
        "choices_field": "choices",
        "label_field": "gold",
        "label_type": "index",
    }
    ex = {"query": "Q?", "choices": ["A", "B", "C"], "gold": 1}
    adapted = adapt_example(ex, 0, ds_cfg)
    assert adapted is not None
    assert adapted.label == "B"
    assert adapted.choices == ["A", "B", "C"]


def test_adapt_example_letter_label():
    """String labels that match choice letters should be preserved."""
    ds_cfg = {
        "name": "toy",
        "task_type": "multiple_choice",
        "question_field": "query",
        "choices_field": "choices",
        "label_field": "gold",
        "label_type": "string",
    }
    ex = {"query": "Q?", "choices": ["A", "B", "C"], "gold": "C"}
    adapted = adapt_example(ex, 0, ds_cfg)
    assert adapted is not None
    assert adapted.label == "C"
