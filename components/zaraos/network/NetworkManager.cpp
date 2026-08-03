#include "network/NetworkManager.h"
#include <esp_log.h>
namespace zara::network {
static constexpr const char* TAG = "NetworkManager";
esp_err_t NetworkManager::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t NetworkManager::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string NetworkManager::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
