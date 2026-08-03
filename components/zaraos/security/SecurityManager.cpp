#include "security/SecurityManager.h"
#include <esp_log.h>
namespace zara::security {
static constexpr const char* TAG = "SecurityManager";
esp_err_t SecurityManager::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t SecurityManager::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string SecurityManager::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
