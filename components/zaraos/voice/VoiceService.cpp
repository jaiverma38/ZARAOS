#include "voice/VoiceService.h"
#include <esp_log.h>
namespace zara::voice {
static constexpr const char* TAG = "VoiceService";
esp_err_t VoiceService::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t VoiceService::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string VoiceService::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
