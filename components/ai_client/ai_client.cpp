#include "ai_client.h"
#include <cJSON.h>
#include <esp_check.h>
#include <esp_crt_bundle.h>
#include <esp_http_client.h>
#include <esp_log.h>
#include <esp_timer.h>
#include <mbedtls/base64.h>

namespace zara::ai_client {
namespace {
constexpr const char* TAG = "AiClient";
constexpr EventBits_t kConnectedBit = BIT0;
constexpr EventBits_t kStopBit = BIT1;
constexpr size_t kQueueDepth = 8;
constexpr size_t kTaskStack = 8192;
}  // namespace

AiClient::AiClient() : queue_(xQueueCreate(kQueueDepth, sizeof(QueueItem))), events_(xEventGroupCreate()) {}

AiClient::~AiClient() {
  stop();
  if (queue_) vQueueDelete(queue_);
  if (events_) vEventGroupDelete(events_);
}

esp_err_t AiClient::configure(const AiServerConfig& config) {
  config_ = config;
  return validate_config();
}

esp_err_t AiClient::validate_config() const {
  if (config_.https_base_url.empty() || config_.device_id.empty()) return ESP_ERR_INVALID_ARG;
  if (config_.jwt_token.empty()) return ESP_ERR_INVALID_STATE;
  return ESP_OK;
}

esp_err_t AiClient::start() {
  ESP_RETURN_ON_ERROR(validate_config(), TAG, "invalid AI cloud configuration");
  if (running_) return ESP_OK;
  running_ = true;
  xEventGroupClearBits(events_, kStopBit);
  xEventGroupSetBits(events_, kConnectedBit);
  BaseType_t ok = xTaskCreate(&AiClient::task_entry, "zara_ai_client", kTaskStack, this, 5, &task_);
  return ok == pdPASS ? ESP_OK : ESP_ERR_NO_MEM;
}

esp_err_t AiClient::stop() {
  if (!running_) return ESP_OK;
  running_ = false;
  xEventGroupSetBits(events_, kStopBit);
  task_ = nullptr;
  return ESP_OK;
}

esp_err_t AiClient::enqueue(const AiRequest& request, TickType_t timeout) {
  QueueItem item{request};
  return xQueueSend(queue_, &item, timeout) == pdTRUE ? ESP_OK : ESP_ERR_TIMEOUT;
}

AiResponse AiClient::request(const AiRequest& request) { return post_json(request); }

void AiClient::set_response_handler(ResponseHandler handler) { response_handler_ = handler; }

bool AiClient::connected() const { return (xEventGroupGetBits(events_) & kConnectedBit) != 0; }

std::string AiClient::status() const { return running_ ? (connected() ? "online" : "reconnecting") : "stopped"; }

void AiClient::task_entry(void* arg) {
  static_cast<AiClient*>(arg)->task_loop();
  vTaskDelete(nullptr);
}

void AiClient::task_loop() {
  QueueItem item{};
  while ((xEventGroupGetBits(events_) & kStopBit) == 0) {
    if (xQueueReceive(queue_, &item, pdMS_TO_TICKS(250)) == pdTRUE) {
      AiResponse response = post_json(item.request);
      if (response_handler_) response_handler_(response);
    }
  }
}

std::string AiClient::endpoint_for(AiMessageType type) const {
  switch (type) {
    case AiMessageType::Chat: return "/v1/llm/chat";
    case AiMessageType::Intent: return "/v1/llm/intent";
    case AiMessageType::VisionFrame: return "/v1/vision/analyze";
    case AiMessageType::FaceEnroll: return "/v1/faces/enroll";
    case AiMessageType::FaceRecognize: return "/v1/faces/recognize";
    case AiMessageType::SttAudio: return "/v1/voice/stt";
    case AiMessageType::TtsRequest: return "/v1/voice/tts";
    case AiMessageType::ToolResult: return "/v1/tools/result";
    case AiMessageType::Health: return "/v1/health";
  }
  return "/v1/health";
}

std::string AiClient::make_envelope(const AiRequest& request) const {
  cJSON* root = cJSON_CreateObject();
  cJSON_AddStringToObject(root, "protocol", kProtocolVersion);
  cJSON_AddStringToObject(root, "device_id", config_.device_id.c_str());
  cJSON_AddStringToObject(root, "correlation_id", request.correlation_id.c_str());
  cJSON_AddStringToObject(root, "locale", request.locale.c_str());
  cJSON_AddNumberToObject(root, "timestamp_ms", static_cast<double>(esp_timer_get_time() / 1000));
  cJSON* payload = request.json_payload.empty() ? cJSON_CreateObject() : cJSON_Parse(request.json_payload.c_str());
  if (!payload) payload = cJSON_CreateObject();
  if (!request.binary_payload.empty()) {
    size_t encoded_len = 0;
    mbedtls_base64_encode(nullptr, 0, &encoded_len, request.binary_payload.data(), request.binary_payload.size());
    std::string encoded(encoded_len, '\0');
    if (mbedtls_base64_encode(reinterpret_cast<unsigned char*>(encoded.data()), encoded.size(), &encoded_len, request.binary_payload.data(), request.binary_payload.size()) == 0) {
      encoded.resize(encoded_len);
      cJSON_AddStringToObject(payload, "binary_base64", encoded.c_str());
      cJSON_AddNumberToObject(payload, "binary_size", static_cast<double>(request.binary_payload.size()));
    }
  }
  cJSON_AddItemToObject(root, "payload", payload);
  char* encoded = cJSON_PrintUnformatted(root);
  std::string out = encoded ? encoded : "{}";
  cJSON_free(encoded);
  cJSON_Delete(root);
  return out;
}

AiResponse AiClient::post_json(const AiRequest& request) {
  AiResponse response{};
  response.correlation_id = request.correlation_id;
  std::string url = config_.https_base_url + endpoint_for(request.type);
  std::string body = make_envelope(request);

  esp_http_client_config_t http_config{};
  http_config.url = url.c_str();
  http_config.timeout_ms = static_cast<int>(config_.request_timeout_ms);
  http_config.crt_bundle_attach = esp_crt_bundle_attach;
  esp_http_client_handle_t client = esp_http_client_init(&http_config);
  if (!client) {
    response.error = "http_client_init_failed";
    xEventGroupClearBits(events_, kConnectedBit);
    return response;
  }

  std::string auth = "Bearer " + config_.jwt_token;
  esp_http_client_set_method(client, HTTP_METHOD_POST);
  esp_http_client_set_header(client, "Content-Type", "application/json");
  esp_http_client_set_header(client, "Authorization", auth.c_str());
  esp_http_client_set_post_field(client, body.c_str(), body.size());

  esp_err_t err = esp_http_client_perform(client);
  response.status_code = esp_http_client_get_status_code(client);
  if (err == ESP_OK && response.status_code >= 200 && response.status_code < 300) {
    int len = esp_http_client_get_content_length(client);
    std::string buffer;
    buffer.resize(len > 0 ? len : 2048);
    int read = esp_http_client_read_response(client, buffer.data(), buffer.size());
    if (read > 0) buffer.resize(read); else buffer.clear();
    response.ok = true;
    response.json_payload = buffer;
    xEventGroupSetBits(events_, kConnectedBit);
  } else {
    response.error = esp_err_to_name(err);
    xEventGroupClearBits(events_, kConnectedBit);
  }
  esp_http_client_cleanup(client);
  return response;
}

}  // namespace zara::ai_client
