from typing import Literal, TypedDict, cast

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.ai.prompts import (
    CLASSIFICATION_PROMPT_TEMPLATE,
    MESSAGE_CLASSIFIER_DESCRIPTION,
    MESSAGE_SUMMARIZER_DESCRIPTION,
    SUMMARIZATION_PROMPT_TEMPLATE,
)
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
        description=MESSAGE_CLASSIFIER_DESCRIPTION,
    )


class MessageSummarizer(BaseModel):
    message_summary: str = Field(
        ...,
        description=MESSAGE_SUMMARIZER_DESCRIPTION,
    )


llm = init_chat_model(model=LLM_MODEL_NAME)
classifier_llm = llm.with_structured_output(MessageClassifier)
summarizer_llm = llm.with_structured_output(MessageSummarizer)


async def summarize_email(state: State) -> dict:
    chain = SUMMARIZATION_PROMPT_TEMPLATE | summarizer_llm
    result = cast(
        MessageSummarizer,
        await chain.ainvoke(
            {
                "subject": state["subject"],
                "body": state["body"],
            }
        ),
    )
    return {"summary": result.message_summary}


async def classify_email(state: State) -> dict:
    chain = CLASSIFICATION_PROMPT_TEMPLATE | classifier_llm
    result = cast(
        MessageClassifier,
        await chain.ainvoke({
            "subject": state["subject"],
            "summary": state["summary"],
        }),
    )
    return {"classification": result.message_classification}


graph_builder = StateGraph(State)

graph_builder.add_node("classify", classify_email)
graph_builder.add_node("summarize", summarize_email)

graph_builder.add_edge(START, "summarize")
graph_builder.add_edge("summarize", "classify")
graph_builder.add_edge("classify", END)

graph = graph_builder.compile()


# open("graph.png", "wb").write(graph.get_graph().draw_mermaid_png())
