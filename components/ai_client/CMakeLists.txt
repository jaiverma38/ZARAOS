idf_component_register(
  SRCS "ai_client.cpp" "ai_manager.cpp"
  INCLUDE_DIRS "."
  REQUIRES esp_http_client esp_event mqtt json nvs_flash esp_timer esp-tls
)
target_compile_features(${COMPONENT_LIB} PUBLIC cxx_std_17)
