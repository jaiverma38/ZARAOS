#pragma once
#include "ai/AiService.h"
#include "audio/AudioService.h"
#include "camera/CameraService.h"
#include "diagnostics/Diagnostics.h"
#include "display/DisplayService.h"
#include "drivers/SensorHub.h"
#include "memory/MemoryStore.h"
#include "mqtt/MqttBridge.h"
#include "network/NetworkManager.h"
#include "ota/OtaManager.h"
#include "robot/RobotController.h"
#include "security/SecurityManager.h"
#include "storage/StorageManager.h"
#include "vision/VisionService.h"
#include "voice/VoiceService.h"
namespace zara {
class Application {
 public:
  esp_err_t start();
 private:
  storage::StorageManager storage_; security::SecurityManager security_; network::NetworkManager network_; mqtt::MqttBridge mqtt_; ota::OtaManager ota_;
  drivers::SensorHub sensors_; audio::AudioService audio_; voice::VoiceService voice_; camera::CameraService camera_; vision::VisionService vision_;
  robot::RobotController robot_; display::DisplayService display_; memory::MemoryStore memory_; ai::AiService ai_; diagnostics::Diagnostics diagnostics_;
};
}
