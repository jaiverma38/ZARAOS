#pragma once
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <freertos/queue.h>
#include <freertos/ringbuf.h>
#include <freertos/semphr.h>
#include <string>
namespace zara::utils {
class Mutex { SemaphoreHandle_t m_; public: Mutex():m_(xSemaphoreCreateMutex()){} ~Mutex(){ if(m_) vSemaphoreDelete(m_);} bool lock(TickType_t t=portMAX_DELAY){return xSemaphoreTake(m_,t)==pdTRUE;} void unlock(){xSemaphoreGive(m_);} };
class Lock { Mutex& m_; public: explicit Lock(Mutex& m):m_(m){m_.lock();} ~Lock(){m_.unlock();} };
class EventBits { EventGroupHandle_t e_; public: EventBits():e_(xEventGroupCreate()){} ~EventBits(){if(e_) vEventGroupDelete(e_);} void set(EventBits_t b){xEventGroupSetBits(e_,b);} void clear(EventBits_t b){xEventGroupClearBits(e_,b);} EventBits_t wait(EventBits_t b, TickType_t t){return xEventGroupWaitBits(e_,b,pdFALSE,pdFALSE,t);} };
}
