#pragma once
#include <driver/gpio.h>
namespace zara::config {
struct Pins {
  static constexpr gpio_num_t I2C_SDA=GPIO_NUM_8, I2C_SCL=GPIO_NUM_9;
  static constexpr gpio_num_t I2S_MIC_WS=GPIO_NUM_4, I2S_MIC_SCK=GPIO_NUM_5, I2S_MIC_SD=GPIO_NUM_6;
  static constexpr gpio_num_t I2S_SPK_BCLK=GPIO_NUM_15, I2S_SPK_LRCLK=GPIO_NUM_16, I2S_SPK_DIN=GPIO_NUM_17;
  static constexpr gpio_num_t MOTOR_L_IN1=GPIO_NUM_10, MOTOR_L_IN2=GPIO_NUM_11, MOTOR_R_IN1=GPIO_NUM_12, MOTOR_R_IN2=GPIO_NUM_13;
  static constexpr gpio_num_t SERVO_NECK=GPIO_NUM_14, BATTERY_ADC=GPIO_NUM_1, CHARGE_DETECT=GPIO_NUM_2;
  static constexpr gpio_num_t CAM_XCLK=GPIO_NUM_21, CAM_PCLK=GPIO_NUM_47, CAM_VSYNC=GPIO_NUM_48, CAM_HREF=GPIO_NUM_45;
};
}
