#include "display/DisplayService.h"
#include <esp_log.h>
namespace zara::display {
static constexpr const char* TAG = "DisplayService";
esp_err_t DisplayService::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t DisplayService::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string DisplayService::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
