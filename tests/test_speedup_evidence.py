import pytest
import speedup_evidence.speedup_evidence as speedup


def test_speedup_success(monkeypatch):

    def fake_sequential(data):
        return {
            "summary": "summary",
            "keywords": "keywords",
            "risks": "risks",
        }

    def fake_parallel(data):
        return {
            "summary": "summary",
            "keywords": "keywords",
            "risks": "risks",
        }

    monkeypatch.setattr(
        speedup,
        "run_sequential",
        fake_sequential,
    )

    monkeypatch.setattr(
        speedup,
        "run_parallel",
        fake_parallel,
    )

    result = speedup.measure_speedup(
        {"text": "Test input"},
        runs=2,
    )

    assert result["runs"] == 2
    assert len(result["sequential_times"]) == 2
    assert len(result["parallel_times"]) == 2

    assert result["average_sequential"] >= 0
    assert result["average_parallel"] >= 0


def test_speedup_failure():

    with pytest.raises(
        ValueError,
        match="Runs must be greater than 0",
    ):
        speedup.measure_speedup(
            {"text": "Test input"},
            runs=0,
        )