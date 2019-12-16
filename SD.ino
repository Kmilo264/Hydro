

#include <SD.h>
 
File logFile; 
int contador;
void setup()
{
  Serial.begin(9600);
  Serial.print("Iniciando SD ...");
  if (!SD.begin(6))
  {
    Serial.println("Error al iniciar");
    return;
  }
  Serial.println("Iniciado correctamente");
}
 
 
// Funcion que simula la lectura de un sensor
int readSensor()
{
   return 0;
}
 
void loop()
{
  // Abrir archivo y escribir valor
  logFile = SD.open("datalog.txt", FILE_WRITE);
  
  if (logFile) { 
        if (logFile) { 
      logFile.print(String(contador)); 
      logFile.print("*");
      logFile.print(String(7.22));
      logFile.print("*");
      logFile.print(String(7.22));
      logFile.print("*");
      logFile.print(String(7.22));
      logFile.print("*");
      //sensor trasero
      logFile.print(String(7.22));
      logFile.print("*");
      logFile.print(String(7.22));
      logFile.print("*");
      logFile.print(String(7.22));
      logFile.print("*");
      //gioscopio
      logFile.print(String(7.22));
      logFile.print("*");
      logFile.print(String(7.22));
      logFile.print("*");
      //Sensor de corriente 
      logFile.print(String(7.22));
      logFile.print("*");
      logFile.print(String(7.22));
      logFile.println(";");
      logFile.close();
  
  } 
  else {
    Serial.println("Error al abrir el archivo");
  }
  contador++;
  delay(100);
  }}
