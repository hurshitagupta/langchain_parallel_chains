import pytest

from merge_logic.merge_logic import merge_results


def test_merge_success():

    data = {
        "branch_one": "HIGH",
        "branch_two": "LOW",
        "branch_three": "LOW",
    }

    result = merge_results(data)

    assert result == "HIGH"


def test_merge_low():

    data = {
        "branch_one": "LOW",
        "branch_two": "LOW",
        "branch_three": "LOW",
    }

    result = merge_results(data)

    assert result == "LOW"


def test_merge_failure():

    with pytest.raises(ValueError):
        merge_results({})