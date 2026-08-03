#include "ai/AiService.h"
#include <esp_log.h>

namespace zara::ai {
namespace {
constexpr const char* TAG = "AiService";
}

esp_err_t AiService::start() {
  running_ = true;
  esp_err_t err = manager_.start();
  if (err == ESP_OK) {
    healthy_ = true;
    owner_registered_ = manager_.owner_exists();
    ESP_LOGI(TAG, "AI cloud online, owner_registered=%d", owner_registered_);
    return ESP_OK;
  }
  healthy_ = true;
  owner_registered_ = false;
  ESP_LOGW(TAG, "AI cloud offline until dashboard provisions secure server config: %s", esp_err_to_name(err));
  return ESP_OK;
}

esp_err_t AiService::stop() {
  running_ = false;
  return manager_.stop();
}

std::optional<ai_client::AiCommand> AiService::handle_text(const std::string& text, const std::string& locale) {
  if (!running_ || !manager_.online()) return std::nullopt;
  ai_client::AiResponse response = manager_.recognize_intent(text, locale);
  if (!response.ok) return std::nullopt;
  return manager_.parse_command(response.json_payload);
}

esp_err_t AiService::save_cloud_config(const ai_client::AiServerConfig& config) {
  esp_err_t err = manager_.save_server_config(config);
  if (err == ESP_OK && running_) err = manager_.start();
  return err;
}

std::string AiService::status() const {
  if (!running_) return "stopped";
  if (!healthy_) return "fault";
  return manager_.online() ? "online" : "offline-local-control";
}

}  // namespace zara::ai
