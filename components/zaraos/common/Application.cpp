#include "common/Application.h"
#include <esp_log.h>
#include <esp_check.h>
#include <nvs_flash.h>
namespace zara {
static constexpr const char* TAG="ZaraOS";
esp_err_t Application::start(){
  esp_err_t err=nvs_flash_init();
  if(err==ESP_ERR_NVS_NO_FREE_PAGES||err==ESP_ERR_NVS_NEW_VERSION_FOUND){ ESP_ERROR_CHECK(nvs_flash_erase()); err=nvs_flash_init(); }
  ESP_RETURN_ON_ERROR(err,TAG,"nvs init failed");
  ESP_RETURN_ON_ERROR(storage_.start(),TAG,"storage"); ESP_RETURN_ON_ERROR(security_.start(),TAG,"security");
  ESP_RETURN_ON_ERROR(network_.start(),TAG,"network"); ESP_RETURN_ON_ERROR(mqtt_.start(),TAG,"mqtt"); ESP_RETURN_ON_ERROR(ota_.start(),TAG,"ota");
  ESP_RETURN_ON_ERROR(sensors_.start(),TAG,"sensors"); ESP_RETURN_ON_ERROR(audio_.start(),TAG,"audio"); ESP_RETURN_ON_ERROR(voice_.start(),TAG,"voice");
  ESP_RETURN_ON_ERROR(camera_.start(),TAG,"camera"); ESP_RETURN_ON_ERROR(vision_.start(),TAG,"vision"); ESP_RETURN_ON_ERROR(robot_.start(),TAG,"robot");
  ESP_RETURN_ON_ERROR(display_.start(),TAG,"display"); ESP_RETURN_ON_ERROR(memory_.start(),TAG,"memory"); ESP_RETURN_ON_ERROR(ai_.start(),TAG,"ai");
  ESP_RETURN_ON_ERROR(diagnostics_.start(),TAG,"diagnostics"); ESP_LOGI(TAG,"ZaraOS online"); return ESP_OK;
}
}
