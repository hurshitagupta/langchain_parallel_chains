import pytest

from determinism.determinism import EXPECTED_ORDER, check_determinism, parallel_chain

def test_output_order():

    result = parallel_chain.invoke(
        {"text": "Test input"}
    )

    assert list(result.keys()) == EXPECTED_ORDER


def test_determinism_across_runs():

    result = check_determinism(runs=5)

    assert result is True


def test_invalid_runs():

    with pytest.raises(
        ValueError,
        match="Runs must be greater than 0",
    ):
        check_determinism(runs=0)