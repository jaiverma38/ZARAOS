# ZaraOS Release Notes

## Current development snapshot

This snapshot advances ZaraOS toward v1.0.0 by adding a runnable AI server fallback, required API contracts, deterministic simulator flow, and validation reports.

### Highlights

- AI server can start with only the Python standard library for local API smoke testing.
- Conversation memory persists user/assistant messages in SQLite.
- First face/frame can enroll the Owner; later recognition compares deterministic embeddings.
- Intent extraction produces robot command payloads for movement and stop commands.
- Simulator validates the voice-to-intent-to-robot path without physical hardware.

### Known limitations

- Firmware build requires an ESP-IDF-enabled environment.
- Heavy AI model packages and model weights could not be installed or downloaded in this container.
- Hardware behavior remains Pending Physical Hardware Validation.
