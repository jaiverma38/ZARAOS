from typing import Any
from pydantic import BaseModel, Field

class ZaraEnvelope(BaseModel):
    protocol: str = Field(default="zaraos.ai.v1")
    device_id: str
    correlation_id: str
    locale: str = "hi-IN"
    timestamp_ms: int | float
    payload: dict[str, Any] = Field(default_factory=dict)

class ApiResponse(BaseModel):
    ok: bool = True
    correlation_id: str
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None

class IntentResult(BaseModel):
    intent: str
    action: str
    confidence: float
    parameters: dict[str, Any] = Field(default_factory=dict)
