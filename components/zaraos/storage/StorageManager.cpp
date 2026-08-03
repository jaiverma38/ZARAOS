#include "storage/StorageManager.h"
#include <esp_log.h>
namespace zara::storage {
static constexpr const char* TAG = "StorageManager";
esp_err_t StorageManager::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t StorageManager::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string StorageManager::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
