from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[ChatTurn] = Field(default_factory=list, max_length=10)


class SourceItem(BaseModel):
    source: str
    page: Optional[int] = 1
    score: Optional[float] = None
    text: Optional[str] = None


class ToolTraceItem(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result_preview: str


class AgentResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = Field(default_factory=list)
    tool_trace: List[ToolTraceItem] = Field(default_factory=list)


class UploadResponse(BaseModel):
    uploaded: List[str]
    chunk_count: int
    message: str


class DocumentListResponse(BaseModel):
    documents: List[str]
    total_count: int


class LogItem(BaseModel):
    timestamp: str
    message: str
    tool_trace: List[ToolTraceItem]
    answer: str


class ErrorResponse(BaseModel):
    detail: str
    error_type: Optional[str] = None
