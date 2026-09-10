from langchain_core.runnables import RunnableLambda, RunnableParallel

from fan_out.fan_out import (summary_chain,keywords_chain)

GAP_MARKER = "<risks unavailable>"

def failing_risks_branch(data: dict) -> str:
    raise ValueError("Risks branch failed")


def risks_fallback(data: dict) -> str:
    return GAP_MARKER


failed_risks_chain = RunnableLambda(
    failing_risks_branch
).with_fallbacks(
    [RunnableLambda(risks_fallback)]
)


fan_out_with_failure = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain,
    risks=failed_risks_chain,
)


def merge_results(data: dict) -> str:
    order = ("summary", "keywords", "risks")

    sections = []

    for key in order:
        value = data.get(key, f"<{key} unavailable>")

        sections.append(
            f"## {key.upper()}\n{value}"
        )

    return "\n\n".join(sections)


partial_failure_chain = (
    fan_out_with_failure
    | RunnableLambda(merge_results)
)


if __name__ == "__main__":

    text = """
    Parallel chains can execute several independent tasks at the
    same time. If one branch fails, the remaining successful
    branches should still be usable.
    """

    result = partial_failure_chain.invoke(
        {"text": text}
    )

    print("\nPARTIAL FAILURE RESULT\n")
    print(result)