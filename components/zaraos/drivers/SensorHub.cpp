#include "drivers/SensorHub.h"
#include <esp_log.h>
namespace zara::drivers {
static constexpr const char* TAG = "SensorHub";
esp_err_t SensorHub::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t SensorHub::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string SensorHub::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
