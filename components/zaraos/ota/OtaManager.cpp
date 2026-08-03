#include "ota/OtaManager.h"
#include <esp_log.h>
namespace zara::ota {
static constexpr const char* TAG = "OtaManager";
esp_err_t OtaManager::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t OtaManager::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string OtaManager::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
