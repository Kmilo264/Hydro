float pinC=A0;
const float Sensibilidad=0.1; //sensibilidad en Voltios/Amperio para sensor de 16A

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(7,OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(7,HIGH);
  float voltajeSensor= analogRead(A0)*(5.0 / 1023.0); //lectura del sensor   
  float I=(voltajeSensor-2.5)/Sensibilidad; //Ecuación  para obtener la corriente
  Serial.print("Voltaje: ");
  Serial.print(voltajeSensor,3);  
  Serial.print("   ");
  Serial.print("Corriente: ");
  Serial.println(I,3);
  //Serial.println(I,3); 
  
  delay(1000);     
}
