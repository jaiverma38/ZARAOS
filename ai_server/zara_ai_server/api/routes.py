import base64
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from zara_ai_server.config import Settings, get_settings
from zara_ai_server.core.media import decode_binary, image_from_payload
from zara_ai_server.schemas import ApiResponse, ZaraEnvelope
from zara_ai_server.security.auth import authenticate
from zara_ai_server.services.runtime import face_engine, llm_engine, memory_store, speech_engine, vision_engine

router = APIRouter(prefix="/v1", dependencies=[Depends(authenticate)])

ZARAOS_ENDPOINTS = [
    "/v1/llm/chat",
    "/v1/llm/intent",
    "/v1/vision/analyze",
    "/v1/faces/enroll",
    "/v1/faces/recognize",
    "/v1/voice/stt",
    "/v1/voice/tts",
]

def parse_request(body: dict[str, Any]) -> ZaraEnvelope:
    if "payload" in body and "device_id" in body:
        return ZaraEnvelope(**body)
    payload = dict(body)
    if "message" in payload and "text" not in payload:
        payload["text"] = payload["message"]
    return ZaraEnvelope(device_id="local-test-device", correlation_id="local", locale=payload.pop("locale", "hi-IN"), timestamp_ms=0, payload=payload)

@router.post("/health", response_model=ApiResponse)
def health(body: dict[str, Any] = Body(default={})) -> ApiResponse:
    envelope = parse_request(body)
    return ApiResponse(correlation_id=envelope.correlation_id, result={"status": "ok", "device_id": envelope.device_id})

@router.post("/llm/chat", response_model=ApiResponse)
def chat(body: dict[str, Any] = Body(...)) -> ApiResponse:
    envelope = parse_request(body)
    text = str(envelope.payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=422, detail="message or payload.text is required")
    answer = llm_engine().chat(text, envelope.locale)
    memory_store().add_memory(envelope.device_id, "conversation", f"User: {text}\nZara: {answer}", {"locale": envelope.locale})
    return ApiResponse(correlation_id=envelope.correlation_id, result={"text": answer})

@router.post("/llm/intent")
def intent(body: dict[str, Any] = Body(...)) -> dict:
    envelope = parse_request(body)
    text = str(envelope.payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=422, detail="message or payload.text is required")
    result = llm_engine().intent(text, envelope.locale)
    result.setdefault("correlation_id", envelope.correlation_id)
    return result

@router.post("/vision/analyze", response_model=ApiResponse)
def analyze_vision(body: dict[str, Any] = Body(...), settings: Settings = Depends(get_settings)) -> ApiResponse:
    envelope = parse_request(body)
    image = image_from_payload(envelope.payload, settings.max_image_bytes)
    prompt = str(envelope.payload.get("prompt", "Describe the scene for robot navigation"))
    result = vision_engine().analyze(image, prompt)
    return ApiResponse(correlation_id=envelope.correlation_id, result=result)

@router.post("/faces/enroll", response_model=ApiResponse)
def enroll_face(body: dict[str, Any] = Body(...), settings: Settings = Depends(get_settings)) -> ApiResponse:
    envelope = parse_request(body)
    image = image_from_payload(envelope.payload, settings.max_image_bytes)
    name = str(envelope.payload.get("name", "Owner"))
    role = str(envelope.payload.get("role", "owner"))
    result = face_engine().enroll(name, image, role)
    return ApiResponse(correlation_id=envelope.correlation_id, result=result)

@router.post("/faces/recognize", response_model=ApiResponse)
def recognize_face(body: dict[str, Any] = Body(...), settings: Settings = Depends(get_settings)) -> ApiResponse:
    envelope = parse_request(body)
    image = image_from_payload(envelope.payload, settings.max_image_bytes)
    result = face_engine().recognize(image)
    return ApiResponse(correlation_id=envelope.correlation_id, result=result)

@router.post("/voice/stt", response_model=ApiResponse)
def stt(body: dict[str, Any] = Body(...), settings: Settings = Depends(get_settings)) -> ApiResponse:
    envelope = parse_request(body)
    audio = decode_binary(envelope.payload, settings.max_audio_bytes)
    if not audio:
        raise HTTPException(status_code=422, detail="audio payload is required")
    result = speech_engine().transcribe(audio)
    return ApiResponse(correlation_id=envelope.correlation_id, result=result)

@router.post("/voice/tts", response_model=ApiResponse)
def tts(body: dict[str, Any] = Body(...)) -> ApiResponse:
    envelope = parse_request(body)
    text = str(envelope.payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=422, detail="message or payload.text is required")
    wav = speech_engine().synthesize(text)
    return ApiResponse(correlation_id=envelope.correlation_id, result={"audio_format": "wav", "audio_base64": base64.b64encode(wav).decode()})
