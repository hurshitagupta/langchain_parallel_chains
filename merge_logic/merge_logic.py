from langchain_core.runnables import RunnableLambda, RunnableParallel


def branch_one(data):
    return "HIGH"


def branch_two(data):
    return "LOW"


def branch_three(data):
    return "LOW"


parallel_chain = RunnableParallel(
    branch_one=RunnableLambda(branch_one),
    branch_two=RunnableLambda(branch_two),
    branch_three=RunnableLambda(branch_three),
)


def merge_results(data):
    if not data:
        raise ValueError("No branch outputs provided")

    values = list(data.values())

    if "HIGH" in values:
        return "HIGH"

    return "LOW"


merge_chain = (
    parallel_chain
    | RunnableLambda(merge_results)
)


if __name__ == "__main__":

    result = merge_chain.invoke(
        {"text": "Payment service issue"}
    )

    print("FINAL MERGED RESULT:")
    print(result)