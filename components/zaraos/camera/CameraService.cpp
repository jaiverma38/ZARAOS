#include "camera/CameraService.h"
#include <esp_log.h>
namespace zara::camera {
static constexpr const char* TAG = "CameraService";
esp_err_t CameraService::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t CameraService::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string CameraService::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
