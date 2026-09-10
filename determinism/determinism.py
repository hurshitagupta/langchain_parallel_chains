from langchain_core.runnables import RunnableLambda, RunnableParallel


EXPECTED_ORDER = ["summary", "keywords", "risks"]
RUNS = 10


def summary_branch(data):
    return "Summary result"


def keywords_branch(data):
    return "Keywords result"


def risks_branch(data):
    return "Risks result"


parallel_chain = RunnableParallel(
    summary=RunnableLambda(summary_branch),
    keywords=RunnableLambda(keywords_branch),
    risks=RunnableLambda(risks_branch),
)


def check_determinism(runs=RUNS):
    if runs <= 0:
        raise ValueError("Runs must be greater than 0")

    all_orders = []

    for run in range(1, runs + 1):
        result = parallel_chain.invoke(
            {"text": "Test input"}
        )

        order = list(result.keys())
        all_orders.append(order)

        print(f"Run {run}: {order}")

    stable = all(
        order == EXPECTED_ORDER
        for order in all_orders
    )

    return stable


if __name__ == "__main__":

    stable = check_determinism()

    print("\nDETERMINISM RESULT")

    if stable:
        print("Output ordering was stable across all runs.")
    else:
        print("Output ordering changed between runs.")