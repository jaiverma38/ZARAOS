#include "robot/RobotController.h"
#include <esp_log.h>
namespace zara::robot {
static constexpr const char* TAG = "RobotController";
esp_err_t RobotController::start() {
  running_ = true; healthy_ = true;
  ESP_LOGI(TAG, "started");
  return ESP_OK;
}
esp_err_t RobotController::stop() {
  running_ = false;
  ESP_LOGI(TAG, "stopped");
  return ESP_OK;
}
std::string RobotController::status() const {
  return running_ ? (healthy_ ? "running" : "fault") : "stopped";
}
}
