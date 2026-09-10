# LangChain Parallel Chains

This project implements parallel chains in LangChain using `RunnableParallel`. The assessment focuses on running independent branches concurrently, measuring parallel execution, handling partial failures, merging branch outputs, and maintaining deterministic output ordering.

## Task 1 — Fan-out

Task 1 implements a fan-out pipeline where the same input is passed to three independent branches using `RunnableParallel`.

The three branches perform different operations:

* **Summary** — summarizes the input text in two short lines.
* **Keywords** — extracts five important keywords.
* **Risks** — identifies two possible risks related to the input.

The branches are combined using:

```python
fan_out_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain,
    risks=risks_chain,
)
```

This allows the three independent chains to process the same input concurrently instead of invoking each chain sequentially.

Each branch follows the same basic LCEL structure:

```text
Input Validation
      ↓
Prompt
      ↓
Model
      ↓
String Output Parser
      ↓
Output Validation
```

The final result from `RunnableParallel` is returned as a dictionary containing the output of all three branches.

Example structure:

```text
{
    "summary": "...",
    "keywords": "...",
    "risks": "..."
}
```

### Guardrails

The implementation includes the required guardrails where applicable:

* **Step limit** — limits the number of model hops allowed per branch.
* **Timeout** — model calls have a configured timeout.
* **Retry** — transient failures use capped retries with exponential jitter.
* **Token budget** — oversized input is rejected before reaching the model.
* **Input validation** — empty or invalid input is rejected.
* **Output validation** — model output is validated before being returned.
* **Output token limit** — model responses have a configured maximum token count.
* **Secret hygiene** — API keys and model configuration are loaded from environment variables.

Shared guardrail logic is kept in `guardrails.py` to avoid duplicating the same logic across tasks.

### Run Task 1

```bash
uv run python -m fan_out.fan_out
```

Save the output:

```bash
uv run python -m fan_out.fan_out > outputs/fan_out.txt
```

### Run Task 1 Tests

```bash
uv run pytest tests/test_fan_out.py -v
```

Save the test output:

```bash
uv run pytest tests/test_fan_out.py -v > outputs/test_fan_out.txt
```

The tests cover a successful three-branch fan-out and rejection of invalid empty input.

---

## Task 2 — Speedup Evidence

Task 2 compares the wall-clock execution time of the same three operations when executed sequentially and in parallel.

The comparison uses the same `summary`, `keywords`, and `risks` chains created in Task 1 so that both approaches perform equivalent work.

### Sequential Execution

The sequential implementation invokes each branch one after another:

```python
def run_sequential(data: dict) -> dict:
    return {
        "summary": summary_chain.invoke(data),
        "keywords": keywords_chain.invoke(data),
        "risks": risks_chain.invoke(data),
    }
```

Each branch must finish before the next branch starts.

### Parallel Execution

The parallel implementation uses the `RunnableParallel` chain created in Task 1:

```python
def run_parallel(data: dict) -> dict:
    return fan_out_chain.invoke(data)
```

Since the three branches are independent, their execution can overlap instead of waiting for each other sequentially.

### Measurement

Both execution methods are measured over **10 runs**.

```python
RUNS = 10
```

Wall-clock time is measured using:

```python
time.perf_counter()
```

For every run, the script records both:

```text
Sequential execution time
Parallel execution time
```

After all 10 runs, average execution times are calculated:

```python
avg_sequential = sum(sequential_times) / runs
avg_parallel = sum(parallel_times) / runs
```

The measured speedup is calculated as:

```python
speedup = avg_sequential / avg_parallel
```

This provides numerical evidence of the difference between sequential and parallel execution rather than assuming that parallel execution is faster.

### Example Output

The script produces output in the following format:

```text
Run 1/10
Sequential: ...
Parallel:   ...

Run 2/10
Sequential: ...
Parallel:   ...

...

Run 10/10
Sequential: ...
Parallel:   ...

=== SPEEDUP SUMMARY ===
Runs: 10
Average sequential time: ...
Average parallel time:   ...
Speedup: ...x
```

The actual measured results are saved in:

```text
outputs/speedup_evidence.txt
```

### Automated Tests

Task 2 contains both a success and failure test.

The success test verifies that:

* the requested number of benchmark runs is completed;
* sequential timings are collected;
* parallel timings are collected;
* average timing values are produced.

The execution functions are monkeypatched during the unit test so that running the test suite does not perform the full real-model benchmark again.

The failure test verifies that an invalid run count such as `0` is rejected.

### Run Task 2

```bash
uv run python -m speedup_evidence.speedup_evidence
```

Save the benchmark evidence:

```bash
uv run python -m speedup_evidence.speedup_evidence > outputs/speedup_evidence.txt
```

### Run Task 2 Tests

```bash
uv run pytest tests/test_speedup_evidence.py -v
```

Save the test output:

```bash
uv run pytest tests/test_speedup_evidence.py -v > outputs/test_speedup_evidence.txt
```

---

## Task 3 — Partial Failure

Task 3 demonstrates how a parallel chain can continue returning useful results even when one independent branch fails.

For this task, the `summary` and `keywords` branches execute normally, while the `risks` branch is deliberately made to fail.

```python
def failing_risks_branch(data: dict) -> str:
    raise ValueError("Risks branch failed")
```

### Handling the Failed Branch

The failing branch uses LangChain's `.with_fallbacks()`:

```python
failed_risks_chain = RunnableLambda(
    failing_risks_branch
).with_fallbacks(
    [RunnableLambda(risks_fallback)]
)
```

If the risks branch fails, its fallback returns an explicit gap marker:

```text
<risks unavailable>
```

This allows the other successful branch outputs to remain available instead of failing the complete parallel chain.

The three branches are executed using:

```python
fan_out_with_failure = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain,
    risks=failed_risks_chain,
)
```

The resulting structure is therefore similar to:

```text
summary  → successful result
keywords → successful result
risks    → failure → fallback → <risks unavailable>
```

### Fan-in and Merge

After the parallel execution finishes, the branch outputs are passed to `merge_results()`.

The reducer keeps the final output in the fixed order:

```text
summary → keywords → risks
```

It also provides an unavailable marker if a branch result is missing.

The complete chain performs both fan-out and fan-in:

```python
partial_failure_chain = (
    fan_out_with_failure | RunnableLambda(merge_results)
)
```

### Automated Tests

Task 3 includes a success case and a failure-path test.

The success test deliberately triggers the risks branch failure and verifies that:

* the final merged result is still returned;
* summary is present;
* keywords are present;
* risks is present;
* the `<risks unavailable>` gap marker is included.

The second test passes incomplete branch data to the merge function and verifies that a missing result is handled using the explicit gap marker instead of raising an error.

### Run Task 3

```bash
uv run python -m partial_failure.partial_failure
```

Save the output:

```bash
uv run python -m partial_failure.partial_failure > outputs/partial_failure.txt
```

### Run Task 3 Tests

```bash
uv run pytest tests/test_partial_failure.py -v
```

Save the test output:

```bash
uv run pytest tests/test_partial_failure.py -v > outputs/test_partial_failure.txt
```

### Task 3 Result

Task 3 demonstrates graceful partial failure within `RunnableParallel`. A deliberately failing branch is recovered using `.with_fallbacks()`, an explicit `<risks unavailable>` marker represents the missing result, and the successful branch outputs are still merged and returned.

---

## Task 4 — Merge Logic

Task 4 implements a reducer that resolves conflicts between parallel branch outputs instead of simply concatenating the results.

For this task, three independent branches are executed using `RunnableParallel`.

The branches return:

```text id="dnn90q"
branch_one   → HIGH
branch_two   → LOW
branch_three → LOW
```

These branch outputs are **intentionally deterministic** for this task. The purpose of Task 4 is to demonstrate and test the conflict-resolution behaviour of the reducer. Using fixed branch outputs makes the conflict reproducible across runs instead of depending on potentially variable model responses.

The previous tasks already demonstrate parallel execution using actual model chains.

### Conflict Resolution

After the parallel branches complete, their results are passed to `merge_results()`.

```python id="1qkgxv"
def merge_results(data):
    if not data:
        raise ValueError("No branch outputs provided")

    values = list(data.values())

    if "HIGH" in values:
        return "HIGH"

    return "LOW"
```

The conflict-resolution rule is intentionally simple:

> If any branch reports `HIGH`, the final merged result is `HIGH`. Otherwise, the result is `LOW`.

For example:

```text id="g7c6a3"
HIGH + LOW + LOW
        ↓
     Reducer
        ↓
       HIGH
```

This is a real merge strategy because the reducer evaluates the branch outputs and produces one resolved result rather than joining the three strings together.

The complete fan-out/fan-in chain is:

```python id="g3k2vl"
merge_chain = ( parallel_chain | RunnableLambda(merge_results))
```

### Automated Tests

Task 4 includes tests for the reducer behaviour.

The tests verify:

* conflicting outputs containing `HIGH` resolve to `HIGH`;
* all `LOW` outputs resolve to `LOW`;
* empty branch output raises a `ValueError`.

This provides deterministic evidence that the reducer follows the defined conflict-resolution rule.

### Run Task 4

```bash id="xt5fsf"
uv run python -m merge_logic.merge_logic
```

Save the output:

```bash id="5j45ui"
uv run python -m merge_logic.merge_logic > outputs/merge_logic.txt
```

### Run Task 4 Tests

```bash id="sf00y1"
uv run pytest tests/test_merge_logic.py -v
```

Save the test output:

```bash id="39uzoh"
uv run pytest tests/test_merge_logic.py -v > outputs/test_merge_logic.txt
```

### Task 4 Result

Task 4 demonstrates conflict resolution during the fan-in stage of a parallel chain. Three deterministic parallel branches intentionally produce conflicting `HIGH` and `LOW` values, and the reducer applies a defined rule to produce one final result.

The deterministic outputs are used specifically to make the merge behaviour reproducible and easy to verify, while actual LLM-based parallel execution is demonstrated in the earlier tasks.

---

## Task 5 — Determinism

Task 5 proves that the output ordering of the parallel chain remains stable across repeated runs.

For this task, three independent branches are executed using `RunnableParallel`:

```python id="i8ggin"
parallel_chain = RunnableParallel(
    summary=RunnableLambda(summary_branch),
    keywords=RunnableLambda(keywords_branch),
    risks=RunnableLambda(risks_branch),
)
```

The expected output order is defined as:

```python id="rqvjhu"
EXPECTED_ORDER = [
    "summary",
    "keywords",
    "risks",
]
```

### Deterministic Branches

The branch outputs are intentionally deterministic for this task.

```text id="gxjtz7"
summary  → Summary result
keywords → Keywords result
risks    → Risks result
```

The purpose of Task 5 is specifically to verify **stable output ordering**, not model response quality or variation. Using deterministic branches isolates the behaviour being tested and makes the result reproducible without depending on external model responses.

Actual model-based parallel execution has already been demonstrated in Tasks 1–3.

### Repeated Execution

The parallel chain is executed **10 times**:

```python id="tbsl4h"
RUNS = 10
```

After each execution, the returned dictionary key order is captured:

```python id="7i0pd4"
order = list(result.keys())
```

Each observed order is then compared against:

```text id="4l1pv8"
summary → keywords → risks
```

The final stability check verifies that every run produced exactly the same ordering.
If all runs match, the script reports that the output ordering remained stable.

### Output Evidence

The script produces output in the following format:

```text id="i5yrra"
Run 1: ['summary', 'keywords', 'risks']
...
Run 10: ['summary', 'keywords', 'risks']

DETERMINISM RESULT
Output ordering was stable across all runs.
```

This provides direct evidence that the parallel execution does not change the expected result ordering between runs.

### Automated Tests

Task 5 includes automated tests covering:

* the returned dictionary follows the expected `summary`, `keywords`, `risks` order;
* ordering remains stable across repeated executions;
* an invalid run count such as `0` raises a `ValueError`.

### Run Task 5

```bash id="2rx9h3"
uv run python -m determinism.determinism
```

Save the output:

```bash id="3t7b4r"
uv run python -m determinism.determinism > outputs/determinism.txt
```

### Run Task 5 Tests

```bash id="k9i8kz"
uv run pytest tests/test_determinism.py -v
```

Save the test output:

```bash id="w6n4ar"
uv run pytest tests/test_determinism.py -v > outputs/test_determinism.txt
```

### Task 5 Result

Task 5 demonstrates deterministic output ordering across repeated `RunnableParallel` executions. The parallel chain was executed 10 times and each run preserved the defined:

```text id="7lks2f"
summary → keywords → risks
```

ordering.

Deterministic branch outputs were intentionally used so that the test focuses specifically on ordering and remains reproducible across executions.

---

## Environment Variables

Model configuration and API credentials are loaded from `.env`.

Example `.env.example`:

No API keys or secrets are stored directly in the source code.


