# ZaraOS

Production ESP-IDF C++17 firmware architecture for an ESP32-S3-WROOM-1 robot with 16 MB flash and 8 MB PSRAM.

## Build

```bash
idf.py set-target esp32s3
idf.py build
```

## Hardware

All GPIO assignments are centralized in `components/zaraos/config/pins.h`; do not hardcode pins in drivers.

## Features

The project is organized into independent components for audio, wake voice, camera/vision, robot motion, sensors, display, AI, persistent memory, security, network, MQTT, OTA, diagnostics, and storage. Runtime code uses ESP-IDF, FreeRTOS primitives, encrypted NVS, LittleFS partitioning, and OTA partitions.
