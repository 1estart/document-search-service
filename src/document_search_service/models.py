from datetime import datetime

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    rubrics: list[str] = Field(default_factory=list)
    text: str
    created_date: datetime


class IndexedDocument(BaseModel):
    id: str
    text: str