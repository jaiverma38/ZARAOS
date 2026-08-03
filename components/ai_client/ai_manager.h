#pragma once
#include "ai_client.h"
#include <esp_err.h>
#include <optional>
#include <string>

namespace zara::ai_client {

class AiManager {
 public:
  AiManager();
  ~AiManager();

  esp_err_t start();
  esp_err_t stop();
  esp_err_t configure_from_nvs();
  esp_err_t save_server_config(const AiServerConfig& config);

  AiResponse chat(const std::string& text, const std::string& locale);
  AiResponse recognize_intent(const std::string& text, const std::string& locale);
  AiResponse analyze_image(const std::vector<uint8_t>& jpeg, const std::string& prompt);
  AiResponse enroll_owner(const std::string& owner_name, const std::vector<uint8_t>& jpeg);

  bool owner_exists() const;
  esp_err_t save_owner_profile(const OwnerProfile& profile);
  std::optional<OwnerProfile> load_owner_profile() const;
  AiCommand parse_command(const std::string& json) const;
  bool online() const { return client_.connected(); }
  std::string status() const { return client_.status(); }

 private:
  std::string next_correlation_id() const;
  AiRequest make_text_request(AiMessageType type, const std::string& text, const std::string& locale) const;
  AiClient client_;
};

}  // namespace zara::ai_client
