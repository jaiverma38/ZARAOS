#include "diagnostics/Diagnostics.h"
#include <esp_log.h>
namespace zara::diagnostics {
static constexpr const char* TAG = "Diagnostics";
esp_err_t Diagnostics::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t Diagnostics::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string Diagnostics::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
