import os

from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openrouter import ChatOpenRouter

from guardrails import (check_step_limit,validate_input,validate_output)


load_dotenv()


model = ChatOpenRouter(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    temperature=0,
    timeout=20_000,
    max_retries=0,
    max_tokens=300,
)

model_with_retry = model.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)

summary_prompt = ChatPromptTemplate.from_template(
    "Summarize the following text in exactly 2 short lines:\n\n{text}"
)

keywords_prompt = ChatPromptTemplate.from_template(
    "Return exactly 5 important keywords from this text, comma separated:\n\n{text}"
)

risks_prompt = ChatPromptTemplate.from_template(
    "Identify exactly 2 possible risks related to this text:\n\n{text}"
)


def prepare_input(data: dict) -> dict:
    text = validate_input(data.get("text", ""))

    check_step_limit(1)

    return {"text": text}


def validate_branch_output(output: str) -> str:
    return validate_output(output)


summary_chain = (
    RunnableLambda(prepare_input) | summary_prompt | model_with_retry | StrOutputParser() | RunnableLambda(validate_branch_output)
)


keywords_chain = (
    RunnableLambda(prepare_input) | keywords_prompt | model_with_retry | StrOutputParser() | RunnableLambda(validate_branch_output)
)


risks_chain = (
    RunnableLambda(prepare_input)| risks_prompt | model_with_retry | StrOutputParser() | RunnableLambda(validate_branch_output)
)


fan_out_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keywords_chain,
    risks=risks_chain,
)


if __name__ == "__main__":

    text = """
    LangChain applications can use RunnableParallel to send the same
    input to multiple independent branches. These branches execute
    concurrently and their results are returned together.
    """

    result = fan_out_chain.invoke({"text": text})

    print("\nPARALLEL RESULT\n")

    print("SUMMARY:")
    print(result["summary"])

    print("\nKEYWORDS:")
    print(result["keywords"])

    print("\nRISKS:")
    print(result["risks"])