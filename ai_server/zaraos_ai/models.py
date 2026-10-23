from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    ready = "ready"
    degraded = "degraded"
    unavailable = "unavailable"


class HealthResponse(BaseModel):
    status: PipelineStatus
    components: dict[str, PipelineStatus]


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    owner_id: str | None = None


class ChatResponse(BaseModel):
    text: str
    model: str
    memory_refs: list[str] = Field(default_factory=list)
    robot_command: dict[str, Any] | None = None


class IntentRequest(BaseModel):
    text: str = Field(min_length=1)


class IntentResponse(BaseModel):
    name: str
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    robot_command: dict[str, Any] | None = None


class VisionFrameRequest(BaseModel):
    camera_id: str = "esp32s3"
    image_base64: str = Field(min_length=1)


class VisionAnalyzeRequest(BaseModel):
    image_base64: str = Field(min_length=1)


class FaceEnrollRequest(VisionAnalyzeRequest):
    name: str = "Owner"


class FaceIdentity(BaseModel):
    id: str
    name: str
    owner: bool = False
    confidence: float = Field(ge=0.0, le=1.0)


class VisionResponse(BaseModel):
    owner_enrolled: bool = False
    faces: list[FaceIdentity] = Field(default_factory=list)
    objects: list[dict[str, Any]] = Field(default_factory=list)
    ocr_text: list[str] = Field(default_factory=list)


class SttRequest(BaseModel):
    audio_base64: str = Field(min_length=1)
    sample_rate: int = 16000


class SttResponse(BaseModel):
    text: str
    engine: str
    status: str


class TtsRequest(BaseModel):
    text: str = Field(min_length=1)
    voice: str = "default"


class TtsResponse(BaseModel):
    audio_base64: str
    engine: str
    sample_rate: int
    status: str


class ModelStatus(BaseModel):
    installed: bool
    status: str
    detail: str | None = None


class SimulatorRequest(BaseModel):
    audio_base64: str = Field(min_length=1)
    image_base64: str = Field(min_length=1)


class ModelVerificationResponse(BaseModel):
    models: dict[str, ModelStatus]
