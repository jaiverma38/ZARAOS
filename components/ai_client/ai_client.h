#pragma once
#include "ai_protocol.h"
#include <esp_err.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <freertos/queue.h>
#include <functional>
#include <string>

namespace zara::ai_client {

class AiClient {
 public:
  using ResponseHandler = std::function<void(const AiResponse&)>;

  AiClient();
  ~AiClient();

  AiClient(const AiClient&) = delete;
  AiClient& operator=(const AiClient&) = delete;

  esp_err_t configure(const AiServerConfig& config);
  esp_err_t start();
  esp_err_t stop();
  esp_err_t enqueue(const AiRequest& request, TickType_t timeout);
  AiResponse request(const AiRequest& request);
  void set_response_handler(ResponseHandler handler);
  bool connected() const;
  std::string status() const;

 private:
  struct QueueItem { AiRequest request; };
  static void task_entry(void* arg);
  void task_loop();
  AiResponse post_json(const AiRequest& request);
  std::string endpoint_for(AiMessageType type) const;
  std::string make_envelope(const AiRequest& request) const;
  esp_err_t validate_config() const;

  AiServerConfig config_;
  QueueHandle_t queue_{nullptr};
  EventGroupHandle_t events_{nullptr};
  TaskHandle_t task_{nullptr};
  ResponseHandler response_handler_{};
  bool running_{false};
};

}  // namespace zara::ai_client
