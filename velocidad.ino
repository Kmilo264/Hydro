#include <Arduino.h>

#define SENSOR_PIN  2  // Pin sensor, debe estar asociado a una interrupción

unsigned long rps = 0;  // Revoluciones por segundo
unsigned long m_inicio = 0;  // millis() inicio

void read_isr();  // Función que se llama cuando ocurre la interrupción

void setup() {
  Serial.begin(9600);

  // Configuramos la interrupción
  attachInterrupt(
    digitalPinToInterrupt(SENSOR_PIN),
    read_isr,
    RISING
  );
}

void loop() {
  // Contamos las revoluciones por segundo
  if (millis() - m_inicio >= 1000) {  // cada segundo
    // Desactivamos las interrupciones
    detachInterrupt(
      digitalPinToInterrupt(SENSOR_PIN)
    );

    Serial.println(rps);  // RPS
    Serial.println();
    rps = 0;

    m_inicio = millis();
    attachInterrupt(
      digitalPinToInterrupt(SENSOR_PIN),
      read_isr,
      RISING
    );
  }

}

void read_isr() {
  rps++;
  delayMicroseconds(10);
}