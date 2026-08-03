#pragma once
#include "ai_manager.h"
#include "common/types.h"
#include "utils/rtos.h"
#include <esp_err.h>
#include <optional>
#include <string>

namespace zara::ai {

class AiService {
 public:
  AiService() = default;
  esp_err_t start();
  esp_err_t stop();
  bool healthy() const { return healthy_; }
  bool online() const { return manager_.online(); }
  bool owner_registered() const { return owner_registered_; }
  std::string status() const;
  std::optional<ai_client::AiCommand> handle_text(const std::string& text, const std::string& locale);
  esp_err_t save_cloud_config(const ai_client::AiServerConfig& config);

 private:
  ai_client::AiManager manager_;
  bool running_{false};
  bool healthy_{false};
  bool owner_registered_{false};
};

}  // namespace zara::ai
