#include "ai/AiService.h"
#include <esp_log.h>
namespace zara::ai {
static constexpr const char* TAG = "AiService";
esp_err_t AiService::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t AiService::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string AiService::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
