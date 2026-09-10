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

## Guardrails

The implementation includes the required guardrails where applicable.

* **Step limit** — limits the number of model hops allowed per branch.
* **Timeout** — model calls have a configured timeout to prevent requests from hanging indefinitely.
* **Retry** — transient model failures use capped retries with exponential jitter.
* **Token budget** — oversized input is rejected before being sent to the model.
* **Input validation** — empty or invalid input is rejected.
* **Output validation** — model output is checked before being returned.
* **Output token limit** — model responses have a configured maximum token count.
* **Secret hygiene** — API keys and model configuration are loaded from environment variables and are not stored directly in source code.

Shared validation and guardrail logic is kept in `guardrails.py` to avoid duplicating the same logic across assessment tasks.

## Environment Variables

Model configuration and API credentials are loaded from a `.env` file.

## Run Task 1

Run the fan-out implementation from the project root:

```bash
uv run python -m fan_out.fan_out
```

Save the output as evidence:

```bash
uv run python -m fan_out.fan_out > outputs/fan_out.txt
```

## Run Tests

Run the Task 1 automated tests:

```bash
uv run pytest tests/test_fan_out.py -v
```

Save the test output:

```bash
uv run pytest tests/test_fan_out.py -v > outputs/test_fan_out.txt
```

The tests cover:

* **Success case** — verifies that the `summary`, `keywords`, and `risks` branches all return non-empty results.
* **Failure case** — verifies that invalid empty input is rejected before reaching the model.

## Task 1 Result

Task 1 demonstrates a working fan-out pipeline using LangChain's `RunnableParallel`.

The same input is distributed to three independent LLM branches, and the outputs are collected into a single structured dictionary. Input/output validation, token limits, retries, timeout configuration, step limiting, and environment-based secret management are also included around the parallel pipeline.
