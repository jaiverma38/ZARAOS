#include "vision/VisionService.h"
#include <esp_log.h>
namespace zara::vision {
static constexpr const char* TAG = "VisionService";
esp_err_t VisionService::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t VisionService::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string VisionService::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
