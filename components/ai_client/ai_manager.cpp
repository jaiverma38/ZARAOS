#include "ai_manager.h"
#include <cJSON.h>
#include <esp_check.h>
#include <esp_log.h>
#include <esp_timer.h>
#include <nvs.h>
#include <memory>

namespace zara::ai_client {
namespace {
constexpr const char* TAG = "AiManager";
constexpr const char* NS = "zara_ai";
constexpr const char* KEY_URL = "https_url";
constexpr const char* KEY_MQTT = "mqtt_uri";
constexpr const char* KEY_WS = "ws_url";
constexpr const char* KEY_JWT = "jwt";
constexpr const char* KEY_DEVICE = "device_id";
constexpr const char* KEY_OWNER_ID = "owner_id";
constexpr const char* KEY_OWNER_NAME = "owner_name";
constexpr const char* KEY_OWNER_EMB = "owner_emb";
constexpr const char* KEY_OWNER_AT = "owner_at";
constexpr const char* KEY_OWNER_SEEN = "owner_seen";
struct NvsCloser { void operator()(nvs_handle_t* h) const { if (h) { nvs_close(*h); delete h; } } };
using NvsHandle = std::unique_ptr<nvs_handle_t, NvsCloser>;
esp_err_t open_nvs(NvsHandle& out) {
  auto raw = std::make_unique<nvs_handle_t>();
  esp_err_t err = nvs_open(NS, NVS_READWRITE, raw.get());
  if (err == ESP_OK) out.reset(raw.release());
  return err;
}
std::string get_string(nvs_handle_t h, const char* key) {
  size_t len = 0;
  if (nvs_get_str(h, key, nullptr, &len) != ESP_OK || len == 0) return {};
  std::string value(len, '\0');
  if (nvs_get_str(h, key, value.data(), &len) != ESP_OK) return {};
  if (!value.empty() && value.back() == '\0') value.pop_back();
  return value;
}
}  // namespace

AiManager::AiManager() = default;
AiManager::~AiManager() { stop(); }

esp_err_t AiManager::start() {
  ESP_RETURN_ON_ERROR(configure_from_nvs(), TAG, "AI config missing");
  return client_.start();
}

esp_err_t AiManager::stop() { return client_.stop(); }

esp_err_t AiManager::save_server_config(const AiServerConfig& config) {
  NvsHandle nvs;
  ESP_RETURN_ON_ERROR(open_nvs(nvs), TAG, "open nvs");
  ESP_RETURN_ON_ERROR(nvs_set_str(*nvs, KEY_URL, config.https_base_url.c_str()), TAG, "url");
  ESP_RETURN_ON_ERROR(nvs_set_str(*nvs, KEY_MQTT, config.mqtt_uri.c_str()), TAG, "mqtt");
  ESP_RETURN_ON_ERROR(nvs_set_str(*nvs, KEY_WS, config.websocket_url.c_str()), TAG, "ws");
  ESP_RETURN_ON_ERROR(nvs_set_str(*nvs, KEY_JWT, config.jwt_token.c_str()), TAG, "jwt");
  ESP_RETURN_ON_ERROR(nvs_set_str(*nvs, KEY_DEVICE, config.device_id.c_str()), TAG, "device");
  ESP_RETURN_ON_ERROR(nvs_commit(*nvs), TAG, "commit");
  return client_.configure(config);
}

esp_err_t AiManager::configure_from_nvs() {
  NvsHandle nvs;
  ESP_RETURN_ON_ERROR(open_nvs(nvs), TAG, "open nvs");
  AiServerConfig cfg;
  cfg.https_base_url = get_string(*nvs, KEY_URL);
  cfg.mqtt_uri = get_string(*nvs, KEY_MQTT);
  cfg.websocket_url = get_string(*nvs, KEY_WS);
  cfg.jwt_token = get_string(*nvs, KEY_JWT);
  cfg.device_id = get_string(*nvs, KEY_DEVICE);
  return client_.configure(cfg);
}

std::string AiManager::next_correlation_id() const { return std::to_string(static_cast<unsigned long long>(esp_timer_get_time())); }

AiRequest AiManager::make_text_request(AiMessageType type, const std::string& text, const std::string& locale) const {
  cJSON* root = cJSON_CreateObject();
  cJSON_AddStringToObject(root, "text", text.c_str());
  cJSON_AddStringToObject(root, "personality", "warm Hindi-English-Hinglish robot companion named Zara");
  cJSON_AddStringToObject(root, "wake_phrase", kWakePhrase);
  char* encoded = cJSON_PrintUnformatted(root);
  AiRequest request;
  request.type = type;
  request.correlation_id = next_correlation_id();
  request.locale = locale;
  request.json_payload = encoded ? encoded : "{}";
  cJSON_free(encoded);
  cJSON_Delete(root);
  return request;
}

AiResponse AiManager::chat(const std::string& text, const std::string& locale) { return client_.request(make_text_request(AiMessageType::Chat, text, locale)); }
AiResponse AiManager::recognize_intent(const std::string& text, const std::string& locale) { return client_.request(make_text_request(AiMessageType::Intent, text, locale)); }

AiResponse AiManager::analyze_image(const std::vector<uint8_t>& jpeg, const std::string& prompt) {
  cJSON* root = cJSON_CreateObject();
  cJSON_AddStringToObject(root, "prompt", prompt.c_str());
  cJSON_AddNumberToObject(root, "image_bytes", static_cast<double>(jpeg.size()));
  char* encoded = cJSON_PrintUnformatted(root);
  AiRequest request{AiMessageType::VisionFrame, next_correlation_id(), "en-US", encoded ? encoded : "{}", jpeg};
  cJSON_free(encoded);
  cJSON_Delete(root);
  return client_.request(request);
}

AiResponse AiManager::enroll_owner(const std::string& owner_name, const std::vector<uint8_t>& jpeg) {
  cJSON* root = cJSON_CreateObject();
  cJSON_AddStringToObject(root, "role", "owner");
  cJSON_AddStringToObject(root, "name", owner_name.c_str());
  cJSON_AddNumberToObject(root, "image_bytes", static_cast<double>(jpeg.size()));
  char* encoded = cJSON_PrintUnformatted(root);
  AiRequest request{AiMessageType::FaceEnroll, next_correlation_id(), "en-US", encoded ? encoded : "{}", jpeg};
  cJSON_free(encoded);
  cJSON_Delete(root);
  return client_.request(request);
}

bool AiManager::owner_exists() const { return load_owner_profile().has_value(); }

esp_err_t AiManager::save_owner_profile(const OwnerProfile& profile) {
  if (profile.owner_id.empty() || profile.face_embedding.empty()) return ESP_ERR_INVALID_ARG;
  NvsHandle nvs;
  ESP_RETURN_ON_ERROR(open_nvs(nvs), TAG, "open nvs");
  ESP_RETURN_ON_ERROR(nvs_set_str(*nvs, KEY_OWNER_ID, profile.owner_id.c_str()), TAG, "owner id");
  ESP_RETURN_ON_ERROR(nvs_set_str(*nvs, KEY_OWNER_NAME, profile.owner_name.c_str()), TAG, "owner name");
  ESP_RETURN_ON_ERROR(nvs_set_blob(*nvs, KEY_OWNER_EMB, profile.face_embedding.data(), profile.face_embedding.size() * sizeof(float)), TAG, "embedding");
  ESP_RETURN_ON_ERROR(nvs_set_i64(*nvs, KEY_OWNER_AT, profile.registered_at_ms), TAG, "registered");
  ESP_RETURN_ON_ERROR(nvs_set_i64(*nvs, KEY_OWNER_SEEN, profile.last_seen_ms), TAG, "seen");
  return nvs_commit(*nvs);
}

std::optional<OwnerProfile> AiManager::load_owner_profile() const {
  NvsHandle nvs;
  if (open_nvs(nvs) != ESP_OK) return std::nullopt;
  OwnerProfile profile;
  profile.owner_id = get_string(*nvs, KEY_OWNER_ID);
  if (profile.owner_id.empty()) return std::nullopt;
  profile.owner_name = get_string(*nvs, KEY_OWNER_NAME);
  size_t emb_len = 0;
  if (nvs_get_blob(*nvs, KEY_OWNER_EMB, nullptr, &emb_len) != ESP_OK || emb_len == 0) return std::nullopt;
  profile.face_embedding.resize(emb_len / sizeof(float));
  if (nvs_get_blob(*nvs, KEY_OWNER_EMB, profile.face_embedding.data(), &emb_len) != ESP_OK) return std::nullopt;
  nvs_get_i64(*nvs, KEY_OWNER_AT, &profile.registered_at_ms);
  nvs_get_i64(*nvs, KEY_OWNER_SEEN, &profile.last_seen_ms);
  profile.active = true;
  return profile;
}

AiCommand AiManager::parse_command(const std::string& json) const {
  AiCommand command;
  command.raw_json = json;
  cJSON* root = cJSON_Parse(json.c_str());
  if (!root) return command;
  cJSON* action = cJSON_GetObjectItem(root, "action");
  std::string act = cJSON_IsString(action) && action->valuestring ? action->valuestring : "";
  if (act == "move") command.action = AiActionType::Move;
  else if (act == "follow_user") command.action = AiActionType::FollowUser;
  else if (act == "come_here") command.action = AiActionType::ComeHere;
  else if (act == "go_back") command.action = AiActionType::GoBack;
  else if (act == "rotate") command.action = AiActionType::Rotate;
  else if (act == "return_home") command.action = AiActionType::ReturnHome;
  else if (act == "stop") command.action = AiActionType::Stop;
  cJSON* direction = cJSON_GetObjectItem(root, "direction");
  if (cJSON_IsString(direction)) command.direction = direction->valuestring;
  cJSON* speed = cJSON_GetObjectItem(root, "speed");
  if (cJSON_IsNumber(speed)) command.speed_percent = speed->valueint;
  cJSON* duration = cJSON_GetObjectItem(root, "duration_ms");
  if (cJSON_IsNumber(duration)) command.duration_ms = duration->valueint;
  cJSON_Delete(root);
  return command;
}

}  // namespace zara::ai_client
