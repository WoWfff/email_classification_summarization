from typing import Literal, TypedDict, cast

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.config import LLM_MODEL_NAME


class State(TypedDict):
    subject: str
    body: str
    classification: str | None
    summary: str | None


class MessageClassifier(BaseModel):
    message_classification: Literal[
        "notification",
        "promotion",
        "user-action",
        "system-alert",
        "newsletter",
    ] = Field(
        ...,
        description=(
            """Classification of the incoming message.
            'notification' represents informational updates sent to users,
            such as order confirmations or account changes.
            'promotion' represents marketing or advertising content intended
            to promote products, services, or campaigns.
            'user-action' represents messages triggered directly by user actions,
            such as sign-ups, purchases, or password reset requests.
            'system-alert' represents technical or operational alerts related
            to system status, failures, or monitoring events.
            'newsletter' represents recurring editorial or content-based emails
            such as digests, news updates, or educational content."""
        ),
    )


class MessageSummarizer(BaseModel):
    message_summary: str = Field(
        ...,
        description=(
            "A concise natural-language summary of the incoming email message. "
            "The summary should capture the main purpose, key information, "
            "important actions, and overall context of the message in 1-3 sentences. "
            "Avoid unnecessary details, formatting, or repetition."
        ),
    )


llm = init_chat_model(model=LLM_MODEL_NAME)
classifier_llm = llm.with_structured_output(MessageClassifier)
summarizer_llm = llm.with_structured_output(MessageSummarizer)


async def summarize_email(state: State) -> dict:
    result = cast(
        MessageSummarizer,
        await summarizer_llm.ainvoke(
            [
                {
                    "role": "system",
                    "content": """
                        You are an email summarization assistant.

                        Your task is to generate a concise and clear summary of the incoming email.

                        Requirements:
                        - Summarize the main purpose and important details of the email.
                        - Include key actions, requests, deadlines, or important context if present.
                        - Keep the summary brief and informative.
                        - Use neutral and professional language.
                        - Do not repeat unnecessary details or copy large parts of the original message.
                        - The summary should be understandable without reading the full email.

                        Return only the summary.
                        """,
                },
                {
                    "role": "user",
                    "content": state["body"],
                },
            ]
        ),
    )

    return {"summary": result.message_summary}


async def classify_email(state: State) -> dict:
    result = cast(
        MessageClassifier,
        await classifier_llm.ainvoke(
            [
                {
                    "role": "system",
                    "content": """
                    You are an email classification assistant.

                    Classify the incoming email into exactly one of the following categories:

                    - 'notification':
                    Informational messages sent to users, such as account updates,
                    confirmations, reminders, or status changes.

                    - 'promotion':
                    Marketing or advertising emails intended to promote products,
                    services, discounts, campaigns, or special offers.

                    - 'user-action':
                    Messages triggered directly by a user action, such as registration,
                    password reset requests, purchases, or account verification.

                    - 'system-alert':
                    Technical, operational, or monitoring-related alerts, including
                    failures, outages, security warnings, or infrastructure events.

                    - 'newsletter':
                    Recurring editorial or informational content such as news digests,
                    product updates, educational content, or periodic summaries.

                    Return only the classification label.
                    """,
                },
                {
                    "role": "user",
                    "content": state["body"],
                },
            ]
        ),
    )

    return {"classification": result.message_classification}


graph_builder = StateGraph(State)

graph_builder.add_node("classify", classify_email)
graph_builder.add_node("summarize", summarize_email)

graph_builder.add_edge(START, "classify")
graph_builder.add_edge(START, "summarize")
graph_builder.add_edge("classify", END)
graph_builder.add_edge("summarize", END)

graph = graph_builder.compile()


# open("graph.png", "wb").write(graph.get_graph().draw_mermaid_png())
