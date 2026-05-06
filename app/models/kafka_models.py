from pydantic import BaseModel


class InputMessage(BaseModel):
    recipients: list[str]
    subject: str
    body_blob_path: str


class ClassificationResult(BaseModel):
    recipients: list[str]
    subject: str
    classification: str | None = None


class SummarizationResult(BaseModel):
    recipients: list[str]
    subject: str
    summary: str | None = None
