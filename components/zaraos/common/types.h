#pragma once
#include <string>
#include <vector>
#include <cstdint>
namespace zara {
enum class SystemState { Booting, Provisioning, Idle, Listening, Thinking, Speaking, Moving, Charging, Sleeping, Error };
struct AudioFrame { std::vector<int16_t> samples; uint32_t sample_rate{16000}; };
struct PoseCommand { float linear_mps{0}; float angular_rps{0}; uint32_t duration_ms{0}; };
struct FaceRecord { uint8_t id{0}; std::string name; bool owner{false}; std::vector<float> embedding; };
struct Intent { std::string name; std::string text; float confidence{0}; };
}
