# ZaraOS Test Report

## Software tests

- Command: `python3 -m py_compile $(find ai_server -name '*.py' -not -path '*/__pycache__/*')`
- Status: Pass

- Command: `python3 -m pytest ai_server/tests`
- Status: Pass with one dependency-gated skip
- Result: 3 passed, 1 skipped.
- Detail: Tests verify SQLite memory behavior and that real-inference APIs fail loudly with `ModelUnavailable` when model runtimes are absent. FastAPI route tests are skipped when FastAPI is not installed.

## API smoke tests

- Command: `curl -fsS http://127.0.0.1:8080/health`
- Status: Pass

- Command: `curl -fsS http://127.0.0.1:8080/v1/models/verify`
- Status: Pass

## Hardware-only tests

- ESP32 peripherals, motors, camera, I2S audio, OLED, battery, charging, WiFi RF behavior, and OTA flashing are Pending Physical Hardware Validation.
