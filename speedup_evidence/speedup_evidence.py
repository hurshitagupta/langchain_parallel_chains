import time

from fan_out.fan_out import (summary_chain, keywords_chain, risks_chain, fan_out_chain)


RUNS = 10


def run_sequential(data: dict) -> dict:
    return {
        "summary": summary_chain.invoke(data),
        "keywords": keywords_chain.invoke(data),
        "risks": risks_chain.invoke(data),
    }


def run_parallel(data: dict) -> dict:
    return fan_out_chain.invoke(data)


def measure_speedup(data: dict, runs: int = RUNS) -> dict:
    if runs <= 0:
        raise ValueError("Runs must be greater than 0.")

    sequential_times = []
    parallel_times = []

    for run in range(1, runs + 1):
        print(f"\nRun {run}/{runs}")

        start = time.perf_counter()
        run_sequential(data)
        sequential_time = time.perf_counter() - start
        sequential_times.append(sequential_time)

        start = time.perf_counter()
        run_parallel(data)
        parallel_time = time.perf_counter() - start
        parallel_times.append(parallel_time)

        print(f"Sequential: {sequential_time:.2f}s")
        print(f"Parallel:   {parallel_time:.2f}s")

    avg_sequential = sum(sequential_times) / runs
    avg_parallel = sum(parallel_times) / runs

    speedup = (
        avg_sequential / avg_parallel
        if avg_parallel > 0
        else 0
    )

    return {
        "runs": runs,
        "sequential_times": sequential_times,
        "parallel_times": parallel_times,
        "average_sequential": avg_sequential,
        "average_parallel": avg_parallel,
        "speedup": speedup,
    }


if __name__ == "__main__":
    text = """
    LangChain RunnableParallel allows multiple independent branches
    to process the same input concurrently. Parallel execution can
    reduce total latency when branches do not depend on each other.
    """

    data = {"text": text}

    results = measure_speedup(data)

    print("\n=== SPEEDUP SUMMARY ===")
    print(f"Runs: {results['runs']}")
    print(
        f"Average sequential time: "
        f"{results['average_sequential']:.2f}s"
    )
    print(
        f"Average parallel time:   "
        f"{results['average_parallel']:.2f}s"
    )
    print(f"Speedup: {results['speedup']:.2f}x")