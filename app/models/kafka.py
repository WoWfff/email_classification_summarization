import uuid

from pydantic import BaseModel, Field


class InputMessage(BaseModel):
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    recipients: list[str]
    subject: str
    body_blob_path: str


class ClassificationResult(BaseModel):
    message_id: uuid.UUID
    recipients: list[str]
    subject: str
    classification: str | None = None


class SummarizationResult(BaseModel):
    message_id: uuid.UUID
    recipients: list[str]
    subject: str
    summary: str | None = None
