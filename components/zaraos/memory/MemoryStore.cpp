#include "memory/MemoryStore.h"
#include <esp_log.h>
namespace zara::memory {
static constexpr const char* TAG = "MemoryStore";
esp_err_t MemoryStore::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t MemoryStore::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string MemoryStore::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
