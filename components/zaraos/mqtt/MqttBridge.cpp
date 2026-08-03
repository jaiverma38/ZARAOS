#include "mqtt/MqttBridge.h"
#include <esp_log.h>
namespace zara::mqtt {
static constexpr const char* TAG = "MqttBridge";
esp_err_t MqttBridge::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t MqttBridge::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string MqttBridge::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
