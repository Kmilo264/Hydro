/*
  LoRa Duplex communication

  Sends a message every half second, and polls continually
  for new incoming messages. Implements a one-byte addressing scheme,
  with 0xFF as the broadcast address.

  Uses readString() from Stream class to read payload. The Stream class'
  timeout may affect other functuons, like the radio's callback. For an

  created 28 April 2017
  by Tom Igoe
*/
#include <SPI.h>              // include LoRa libraries
#include <LoRa.h>

//Librerias MPU9250
#include <Wire.h>
#include <MPU6050.h>
#include <MPU9250.h>
MPU6050 mpu;
MPU9250 IMU(Wire,0x69);
int status;
// Timers
unsigned long timer = 0;
float timeStep = 0.01;

// Pitch, Roll and Yaw values
float pitch = 0;
float roll = 0;
float yaw = 0;


//LoRa
const int csPin = 53;          // LoRa radio chip select
const int resetPin = 9;       // LoRa radio reset
const int irqPin = 19;         // change for your board; must be a hardware interrupt pin

String outgoing;              // outgoing message

byte msgCount = 0;            // count of outgoing messages
byte localAddress = 0xCC;     // address of this device
byte destination = 0xBB;      // destination to send to
long lastSendTime = 0;        // last send time
float interval = 2000.23;          // interval between sends

void setup() {
  Serial.begin(115200);                   // initialize serial
  while (!Serial);
  status = IMU.begin();
  if (status < 0) {
  Serial.println("IMU initialization unsuccessful");
  Serial.println("Check IMU wiring or try cycling power");
  Serial.print("Status: ");
  Serial.println(status);
    while(1) {}
  }

  //Acelerometro
  {

  Serial.println("Initialize MPU6050");

  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
    delay(500);
  }
  }

  //LoRa
  Serial.println("LoRa Duplex");

  // override the default CS, reset, and IRQ pins (optional)
  LoRa.setPins(csPin, resetPin, irqPin);// set CS, reset, IRQ pin

  if (!LoRa.begin(915E6)) {             // initialize ratio at 915 MHz
    Serial.println("LoRa init failed. Check your connections.");
    while (true);                       // if failed, do nothing
  }

  Serial.println("LoRa init succeeded.");
}

//Función acelerómetro

void checkSettings()
{
  Serial.println();
  
  Serial.print(" * Sleep Mode:            ");
  Serial.println(mpu.getSleepEnabled() ? "Enabled" : "Disabled");
  
  Serial.print(" * Clock Source:          ");
  switch(mpu.getClockSource())
  {
    case MPU6050_CLOCK_KEEP_RESET:     Serial.println("Stops the clock and keeps the timing generator in reset"); break;
    case MPU6050_CLOCK_EXTERNAL_19MHZ: Serial.println("PLL with external 19.2MHz reference"); break;
    case MPU6050_CLOCK_EXTERNAL_32KHZ: Serial.println("PLL with external 32.768kHz reference"); break;
    case MPU6050_CLOCK_PLL_ZGYRO:      Serial.println("PLL with Z axis gyroscope reference"); break;
    case MPU6050_CLOCK_PLL_YGYRO:      Serial.println("PLL with Y axis gyroscope reference"); break;
    case MPU6050_CLOCK_PLL_XGYRO:      Serial.println("PLL with X axis gyroscope reference"); break;
    case MPU6050_CLOCK_INTERNAL_8MHZ:  Serial.println("Internal 8MHz oscillator"); break;
  }
  
  Serial.print(" * Accelerometer:         ");
  switch(mpu.getRange())
  {
    case MPU6050_RANGE_16G:            Serial.println("+/- 16 g"); break;
    case MPU6050_RANGE_8G:             Serial.println("+/- 8 g"); break;
    case MPU6050_RANGE_4G:             Serial.println("+/- 4 g"); break;
    case MPU6050_RANGE_2G:             Serial.println("+/- 2 g"); break;
  }  

  Serial.print(" * Accelerometer offsets: ");
  Serial.print(mpu.getAccelOffsetX());
  Serial.print(" / ");
  Serial.print(mpu.getAccelOffsetY());
  Serial.print(" / ");
  Serial.println(mpu.getAccelOffsetZ());
  
  Serial.println();
  mpu.calibrateGyro();
  mpu.setThreshold(2);
}

void loop() {

  //Acelerometro
  // read the sensor
  IMU.readSensor();
  // display the data
  Serial.print(" Xnorm1=");  
  Serial.print(IMU.getAccelX_mss(),6);
  Serial.print(" Ynorm= ");
  Serial.print(IMU.getAccelY_mss(),6);
  Serial.print(" Znorm= ");
  Serial.println(IMU.getAccelZ_mss(),6);

  
  timer = millis();
  Vector rawAccel = mpu.readRawAccel();
  Vector normAccel = mpu.readNormalizeAccel();
  Vector norm = mpu.readNormalizeGyro();
  

  Serial.print(" Xnorm = ");
  Serial.print(normAccel.XAxis,6);
  Serial.print(" Ynorm = ");
  Serial.print(normAccel.YAxis,6);
  Serial.print(" Znorm = ");
  Serial.println(normAccel.ZAxis,6);


    // Calculate Pitch, Roll and Yaw
  pitch = pitch + norm.YAxis * timeStep;
  roll = roll + norm.XAxis * timeStep;
  yaw = yaw + norm.ZAxis * timeStep;

  // Output raw
  int roll = -(atan2(normAccel.XAxis, normAccel.ZAxis)*180.0)/M_PI;
  int pitch = (atan2(normAccel.YAxis, normAccel.ZAxis)*180.0)/M_PI;

  // Output
  Serial.print(" Pitch = ");
  Serial.print(pitch);
  Serial.print(" Roll = ");
  Serial.print(roll);
  
  Serial.println();
  //delay(100);

  //LoRa

  
  LoRa.beginPacket();                   // start packet
//Aceleración primer sensor
  LoRa.print("X");
  LoRa.print(normAccel.XAxis,6);
  LoRa.print("*");
  LoRa.print("Y");
  LoRa.print(normAccel.YAxis,6);
  LoRa.print("*");
  LoRa.print("Z");
  LoRa.print(normAccel.ZAxis,6);
  LoRa.print("*");

//Aceleración segundo sensor
  LoRa.print("Xb");  
  LoRa.print(IMU.getAccelX_mss(),6);
  LoRa.print("*");
  LoRa.print("Yb");
  LoRa.print(IMU.getAccelY_mss(),6);
  LoRa.print("*");
  LoRa.print("Zb");
  LoRa.print(IMU.getAccelZ_mss(),6);
  LoRa.print("*");


  //Inclinación

  LoRa.print("P");
  LoRa.print(pitch);
  LoRa.print("*");
  LoRa.print("R");
  LoRa.print(roll); 
  LoRa.println(";");
//  
//  LoRa.write(destination);              // add destination address
//  LoRa.write(localAddress);             // add sender address
//  LoRa.write(msgCount);                 // add message ID
//  LoRa.write(outgoing.length());        // add payload length
//  LoRa.print(outgoing);                 // add payload
  LoRa.endPacket();                     // finish packet and send it
                                  // increment message ID
}
