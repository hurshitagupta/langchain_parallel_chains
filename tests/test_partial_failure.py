import pytest

from partial_failure.partial_failure import (
    GAP_MARKER,
    merge_results,
    partial_failure_chain,
)


def test_partial_failure_success():

    result = partial_failure_chain.invoke(
        {
            "text": (
                "Parallel execution allows independent "
                "operations to run concurrently."
            )
        }
    )

    assert "SUMMARY" in result
    assert "KEYWORDS" in result
    assert "RISKS" in result

    assert GAP_MARKER in result


def test_merge_failure():

    incomplete_data = {
        "summary": "Test summary",
        "keywords": "parallel, chains",
    }

    result = merge_results(incomplete_data)

    assert "<risks unavailable>" in result