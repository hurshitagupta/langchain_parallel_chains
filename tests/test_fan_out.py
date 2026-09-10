import pytest

from fan_out.fan_out import fan_out_chain


def test_fan_out_success():

    result = fan_out_chain.invoke(
        {
            "text": (
                "Parallel chains allow independent operations "
                "to execute concurrently."
            )
        }
    )

    assert "summary" in result
    assert "keywords" in result
    assert "risks" in result

    assert result["summary"].strip()
    assert result["keywords"].strip()
    assert result["risks"].strip()


def test_fan_out_failure():

    with pytest.raises(ValueError, match="Input cannot be empty"):
        fan_out_chain.invoke({"text": ""})