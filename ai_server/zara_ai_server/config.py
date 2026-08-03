from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str = Field(default="dev-only-change-me", alias="ZARA_JWT_SECRET")
    local_testing: bool = Field(default=False, alias="ZARA_LOCAL_TESTING")
    llm_model: str = Field(default="Qwen/Qwen2.5-0.5B-Instruct", alias="ZARA_LLM_MODEL")
    face_model: str = Field(default="buffalo_l", alias="FACE_MODEL")
    vision_model: str = Field(default="yolo11n.pt", alias="VISION_MODEL")
    whisper_model: str = Field(default="base", alias="WHISPER_MODEL")
    piper_model_path: Path = Field(default=Path("models/piper"), alias="PIPER_MODEL_PATH")
    database_url: str = Field(default="sqlite:///zara.db", alias="DATABASE_URL")
    data_dir: Path = Field(default=Path("data"), alias="ZARA_DATA_DIR")
    max_image_bytes: int = Field(default=1_500_000, alias="ZARA_MAX_IMAGE_BYTES")
    max_audio_bytes: int = Field(default=2_000_000, alias="ZARA_MAX_AUDIO_BYTES")
    request_rate_per_minute: int = Field(default=120, alias="ZARA_RATE_PER_MINUTE")

    @property
    def piper_voice(self) -> str:
        if self.piper_model_path.is_file():
            return str(self.piper_model_path)
        return str(self.piper_model_path / "en_US-lessac-medium.onnx")

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.piper_model_path.mkdir(parents=True, exist_ok=True)
    return settings
