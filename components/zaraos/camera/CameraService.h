#pragma once
#include "common/types.h"
#include "utils/rtos.h"
#include <esp_err.h>
#include <string>
namespace zara::camera {
class CameraService {
 public:
  CameraService() = default;
  esp_err_t start();
  esp_err_t stop();
  bool healthy() const { return healthy_; }
  std::string status() const;
 private:
  bool running_{false};
  bool healthy_{false};
};
}
