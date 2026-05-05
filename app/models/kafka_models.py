from pydantic import BaseModel


class InputMessage(BaseModel):
    recipients: list[str]
    subject: str
    body_blob_path: str


class ClassificationResult(BaseModel):
    recipients: list[str]
    subject: str
    classification: dict


class SummarizationResult(BaseModel):
    recipients: list[str]
    subject: str
    summary: str
