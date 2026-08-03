#include "audio/AudioService.h"
#include <esp_log.h>
namespace zara::audio {
static constexpr const char* TAG = "AudioService";
esp_err_t AudioService::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t AudioService::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string AudioService::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
