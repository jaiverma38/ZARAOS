#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace zara::ai_client {

enum class AiMessageType : uint8_t {
  Chat = 1,
  Intent,
  VisionFrame,
  FaceEnroll,
  FaceRecognize,
  SttAudio,
  TtsRequest,
  ToolResult,
  Health,
};

enum class AiActionType : uint8_t {
  None = 0,
  Move,
  FollowUser,
  ComeHere,
  GoBack,
  Rotate,
  ReturnHome,
  Stop,
  Relay,
  Display,
  Speak,
};

struct AiServerConfig {
  std::string https_base_url;
  std::string mqtt_uri;
  std::string websocket_url;
  std::string jwt_token;
  std::string device_id;
  uint32_t request_timeout_ms{15000};
  uint32_t reconnect_backoff_ms{2000};
  uint32_t max_reconnect_backoff_ms{60000};
};

struct AiRequest {
  AiMessageType type{AiMessageType::Health};
  std::string correlation_id;
  std::string locale{"hi-IN"};
  std::string json_payload;
  std::vector<uint8_t> binary_payload;
};

struct AiResponse {
  bool ok{false};
  int status_code{0};
  std::string correlation_id;
  std::string json_payload;
  std::string error;
};

struct AiCommand {
  AiActionType action{AiActionType::None};
  std::string raw_json;
  std::string direction;
  int speed_percent{0};
  int duration_ms{0};
};

struct OwnerProfile {
  std::string owner_id;
  std::string owner_name;
  std::vector<float> face_embedding;
  int64_t registered_at_ms{0};
  int64_t last_seen_ms{0};
  bool active{false};
};

constexpr const char* kProtocolVersion = "zaraos.ai.v1";
constexpr const char* kWakePhrase = "Hey Zara";
constexpr size_t kMaxMembers = 8;

}  // namespace zara::ai_client
