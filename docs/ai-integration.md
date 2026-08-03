# ZaraOS AI Upgrade

ZaraOS now separates embedded real-time duties from cloud AI duties. The ESP32-S3 keeps motor control, sensors, camera capture, audio I/O, display, offline wake/basic commands, MQTT, OTA, and secure storage. The AI server performs LLM reasoning, STT, TTS, face embedding, object detection, OCR, and long-term memory backup.

## Cloud protocol

`components/ai_client` implements the secure AI communication boundary. Every HTTPS request is wrapped with:

- `protocol`: `zaraos.ai.v1`
- `device_id`: provisioned device identity
- `correlation_id`: per-request tracing ID
- `locale`: Hindi, English, or Hinglish routing hint
- `timestamp_ms`: ESP timer timestamp
- `payload`: command-specific JSON

The client validates server certificates through the ESP-IDF certificate bundle and authenticates with a JWT bearer token stored in encrypted NVS.

## Endpoints

| Feature | Endpoint |
| --- | --- |
| LLM chat | `/v1/llm/chat` |
| Intent recognition/tool calling | `/v1/llm/intent` |
| Vision understanding | `/v1/vision/analyze` |
| Owner/member face enrollment | `/v1/faces/enroll` |
| Face recognition | `/v1/faces/recognize` |
| Speech-to-text | `/v1/voice/stt` |
| Text-to-speech | `/v1/voice/tts` |
| Tool result callback | `/v1/tools/result` |
| Health | `/v1/health` |

## Owner security

On boot, `AiService` checks the encrypted AI NVS namespace for an owner profile. If no profile exists, the firmware remains in safe local-control mode until provisioning and enrollment are completed by the dashboard or enrollment flow. Existing owner data is not automatically replaced; new owner registration must be initiated by factory reset, authenticated owner change, or authenticated dashboard action.

## AI command format

The LLM intent endpoint returns JSON such as:

```json
{"action":"move","direction":"forward","speed":50,"duration_ms":1000}
```

or:

```json
{"action":"follow_user"}
```

`AiManager::parse_command()` converts these responses into typed firmware commands for robot modules.

## Offline mode

If AI cloud configuration is missing or WiFi/cloud is unavailable, `AiService` reports `offline-local-control` while preserving boot, motor control, sensors, OLED, OTA, and future local wake/basic-command functionality.
