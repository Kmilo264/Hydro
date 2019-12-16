boolean est = false;
int entrada = A0; //Pin entrada del sensor
int entrada2; 
unsigned long reloj1; //Variables de tiempo para medir las RPM
unsigned long reloj2 = 0;
unsigned long tiempo1;//Variables de tiempo para imprimir las RPM
unsigned long tiempo2=0;
float RPM;
int i; //Variable para solo medir las RPM una vez por flanco

void setup(){
pinMode(entrada, INPUT);
Serial.begin(9600);
}

void loop() {
reloj1 = micros();
entrada2 = analogRead(entrada);
    if(entrada2>200 && i <1){
    tiempo1 = micros();
    RPM = (float)30000000/(tiempo1-tiempo2);
    i = 1;
    }
    else if(entrada2<200 && i == 1){
    tiempo2 = micros();
    RPM = (float)30000000/(tiempo2-tiempo1);
    i = 0;
    }
    if(reloj1-reloj2 >2000000 ){
          Serial.println(RPM);
          reloj2 = reloj1;
      }
}
