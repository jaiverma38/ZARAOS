from __future__ import annotations

from fastapi import FastAPI

from .memory import ConversationMemory
from .models import (
    ChatRequest,
    ChatResponse,
    FaceEnrollRequest,
    HealthResponse,
    IntentRequest,
    IntentResponse,
    ModelVerificationResponse,
    SimulatorRequest,
    SttRequest,
    SttResponse,
    TtsRequest,
    TtsResponse,
    VisionAnalyzeRequest,
    VisionFrameRequest,
    VisionResponse,
)
from .service import ZaraAiService


def create_app(memory: ConversationMemory | None = None) -> FastAPI:
    app = FastAPI(title="ZaraOS AI Server", version="0.2.0")
    app.state.service = ZaraAiService(memory)

    @app.get("/health", response_model=HealthResponse)
    def health() -> dict:
        return app.state.service.health()

    @app.get("/v1/models/verify", response_model=ModelVerificationResponse)
    def verify_models() -> dict:
        return app.state.service.verify_models()

    @app.post("/v1/llm/chat", response_model=ChatResponse)
    @app.post("/v1/chat", response_model=ChatResponse)
    def chat(req: ChatRequest) -> dict:
        return app.state.service.chat(req.session_id, req.text, req.owner_id)

    @app.post("/v1/llm/intent", response_model=IntentResponse)
    def intent(req: IntentRequest) -> dict:
        return app.state.service.intent(req.text)

    @app.post("/v1/faces/enroll", response_model=dict)
    def enroll(req: FaceEnrollRequest) -> dict:
        return app.state.service.enroll_face(req.image_base64, req.name)

    @app.post("/v1/faces/recognize", response_model=VisionResponse)
    def recognize(req: VisionAnalyzeRequest) -> dict:
        return app.state.service.recognize_face(req.image_base64)

    @app.post("/v1/vision/analyze", response_model=VisionResponse)
    @app.post("/v1/vision/frame", response_model=VisionResponse)
    def vision(req: VisionFrameRequest) -> dict:
        return app.state.service.analyze_vision(req.image_base64)

    @app.post("/v1/voice/stt", response_model=SttResponse)
    def stt(req: SttRequest) -> dict:
        return app.state.service.stt(req.audio_base64)

    @app.post("/v1/voice/tts", response_model=TtsResponse)
    def tts(req: TtsRequest) -> dict:
        return app.state.service.tts(req.text)

    @app.post("/v1/simulator/run", response_model=dict)
    def simulate(req: SimulatorRequest) -> dict:
        return app.state.service.simulate(req.audio_base64, req.image_base64)

    return app


app = create_app()
