#include "common/Application.h"
#include <esp_log.h>
extern "C" void app_main(void) {
  static zara::Application app;
  ESP_ERROR_CHECK(app.start());
}
