idf_component_register(
  SRC_DIRS common utils config diagnostics storage security memory network mqtt ota drivers audio voice camera vision robot display ai
  INCLUDE_DIRS .
  REQUIRES esp_wifi esp_event nvs_flash esp_http_client esp_https_ota mqtt driver esp_timer json freertos esp_littlefs
)
target_compile_features(${COMPONENT_LIB} PUBLIC cxx_std_17)
