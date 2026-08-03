from functools import lru_cache
from zara_ai_server.config import get_settings
from zara_ai_server.models.mock import LocalFaceEngine, LocalLlmEngine, LocalMemoryStore, LocalSpeechEngine, LocalVisionEngine

@lru_cache
def memory_store():
    settings = get_settings()
    if settings.local_testing:
        return LocalMemoryStore()
    from zara_ai_server.storage.memory import MemoryStore
    return MemoryStore(settings.data_dir)

@lru_cache
def llm_engine():
    settings = get_settings()
    if settings.local_testing:
        return LocalLlmEngine()
    from zara_ai_server.models.llm import LlmEngine
    return LlmEngine(settings.llm_model)

@lru_cache
def vision_engine():
    settings = get_settings()
    if settings.local_testing:
        return LocalVisionEngine()
    from zara_ai_server.models.vision import VisionEngine
    return VisionEngine(settings.vision_model)

@lru_cache
def face_engine():
    settings = get_settings()
    if settings.local_testing:
        return LocalFaceEngine()
    from zara_ai_server.models.face import FaceEngine
    return FaceEngine(memory_store(), settings.face_model)

@lru_cache
def speech_engine():
    settings = get_settings()
    if settings.local_testing:
        return LocalSpeechEngine()
    from zara_ai_server.models.speech import SpeechEngine
    return SpeechEngine(settings.whisper_model, settings.piper_voice)
