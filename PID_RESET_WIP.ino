//MISMO CÓDIGO, AGREGAMOS UN RESET PARA LA MÁQUINA DE ESTADOS, EL CUAL VIENE 
//DESDE PYTHON
#include <PID_v1_bc.h>
#include <max6675.h>
#include "BTS7960.h"

// ---------------------- TERMOPAR + PID ----------------------
const int thermoDO  = 12;
const int thermoCS  = 10;
const int thermoCLK = 13;
const int ssrPin    = 9;

MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);

// PID
double setpoint = 50.0;
double input = 0.0;
double output = 0.0;

double kp = 4.0, ki = 0.5, kd = 0.2;
PID myPID(&input, &output, &setpoint, kp, ki, kd, DIRECT);

// ---------------------- FILTRO MOVIL ----------------------
const int numReadings = 5;
double readings[numReadings];
int readIndex = 0;
double total = 0.0;

// ---------------------- PWM SSR ----------------------
const unsigned long windowSize = 1000;
unsigned long windowStartTime;

// ---------------------- MOTOR ----------------------
const uint8_t EN    = 8;
const uint8_t L_PWM = 6;
const uint8_t R_PWM = 5;

BTS7960 motorController(EN, L_PWM, R_PWM);

unsigned long motorRunTime = 0; //tIEMPO TOTAL 
unsigned long motorStartMillis = 0; //tIEMPO DE INICIO
unsigned long tiempoRestante = 0;   //TIEMPO CALCULADO
bool motorRunning = false;

String bufferSerial = "";
String cmd = "";
// ---------------------- ESTADOS ----------------------
enum Estado {
  RESET,
  PRECALENTAMIENTO,
  ENFRIANDO,
  ESPERANDO_CONFIRMACION,
  TUESTANDO,
  ERROR_TERMOPAR
};

Estado estadoActual = RESET;

// -----------------------------------------------------
//                    SETUP
// -----------------------------------------------------
void setup() {
  Serial.begin(9600);
  pinMode(ssrPin, OUTPUT);

  // Inicializar filtro
  for (int i = 0; i < numReadings; i++) {
    readings[i] = 0.0;
  }
  total = 0.0;

  myPID.SetOutputLimits(0, windowSize);
  myPID.SetMode(AUTOMATIC);
  myPID.Initialize();

  windowStartTime = millis();
  motorController.Enable();
}

// -----------------------------------------------------
//        LECTURA DEL TERMOPAR CON FILTRO
// -----------------------------------------------------
bool leerTermopar(double &temperatura) {
  double rawTemp = thermocouple.readCelsius();

  if (isnan(rawTemp) || rawTemp > 250 || rawTemp < -10) {
    return false;
  }

  total -= readings[readIndex];
  readings[readIndex] = rawTemp;
  total += rawTemp;

  readIndex = (readIndex + 1) % numReadings;
  temperatura = total / numReadings;

  return true;
}
  // ----------- LECTURA SERIAL  -----------

void leerSerial() {
  while (Serial.available() > 0 ){
    char c = Serial.read();
    
    //Serial.print("RX CHAR: [");
    //Serial.print(c);
    //Serial.println("]");
    
    if (c == '\n' || c == '\r'){
      //Serial.print("RX CHAR: [");
      //Serial.print(c);
      //Serial.println("]");
      bufferSerial.trim();
      procesarComando(bufferSerial);
      bufferSerial = "";
    } else {
      bufferSerial += c;
      }
  } 
}

void procesarComando(String cmd){
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "RESET"){
    estadoActual = RESET;
    Serial.println("ACK:RESET");
  }
// TIEMPOS DEL MOTOR//
  if (estadoActual == PRECALENTAMIENTO ||
      estadoActual == ENFRIANDO ||
      estadoActual == ESPERANDO_CONFIRMACION){
        
      if (cmd == "0"){
        motorController.TurnLeft(0);
        motorRunning = false;
        motorRunTime = 0;
        Serial.println("ACK:MOTOR_DETENIDO");
        return;
      }
      if (cmd == "OCHO_MIN"){
        motorRunTime = 8UL *60000UL;
        Serial.println("ACK:MOTOR_8_MIN");
        return;
      }
      if (cmd == "DIEZ_MIN"){
        motorRunTime = 10UL *60000UL;
        Serial.println("ACK:MOTOR_10_MIN");
        return;
      }
      if (cmd == "DOCE_MIN"){
        motorRunTime = 12UL *60000UL;
        Serial.println("ACK:MOTOR_12_MIN");
        return;
      }
      }

  if (estadoActual == ESPERANDO_CONFIRMACION && cmd == "START"){
    //CHECAMOS QUE HAYA UN MODO DE TUESTE
    if (motorRunTime == 0){
      Serial.println("ERR:NO_MOTOR_TIME");
      return;
    }
    
    windowStartTime = millis();
    motorStartMillis = millis();
    motorRunning = true;
    estadoActual = TUESTANDO;

    Serial.println("ACK:START");
    return;
  }

   if (estadoActual == TUESTANDO &&
      (cmd == "OCHO" || cmd == "DIEZ" || cmd == "DOCE")) {
    Serial.println("ERR:MOTOR_TIME_LOCKED");
    return;
  }

  else if (cmd == "STOP"){
    estadoActual = ENFRIANDO;
    Serial.println("ACK:STOP");
  }
  Serial.println(cmd);
}  

//          TIEMPOOO        //
void actualizarTiempoRestante(){
  if (motorRunning && motorRunTime > 0){
    unsigned long transcurrido = millis() - motorStartMillis;

    if (transcurrido >= motorRunTime) {
      tiempoRestante = 0;
    } else {
      tiempoRestante = motorRunTime - transcurrido;
    }
  } else {
    tiempoRestante = 0; //No hay seleecion del tiempo
  }
}

void printTime(){
  unsigned long seg = tiempoRestante / 1000;
  unsigned int min = seg / 60;
  unsigned int sec = seg % 60;

  Serial.print(" | Tiempo Restante: ");
  Serial.print(min);
  Serial.print("m ");
  Serial.print(sec);
  Serial.print("s");
}
// -----------------------------------------------------
//                    LOOP
// -----------------------------------------------------
void loop() {

  // ----------- TERMOPAR -----------
  double temp;
  if (!leerTermopar(temp)) {
    estadoActual = ERROR_TERMOPAR;
  } else {
    input = temp;
  }

  unsigned long now = millis();
  leerSerial();
  // ----------- MAQUINA DE ESTADOS -----------
  switch (estadoActual) {
    
    case RESET:
    Serial.print("Se inicio el Reset");
    output = 0; //paramos ACTUADOR
    motorController.TurnLeft(0);
    motorRunning = false; //deshabilitamos Motor
    motorRunTime = 0;
    motorStartMillis = 0;
    estadoActual = PRECALENTAMIENTO;


    break;

    case PRECALENTAMIENTO:
      setpoint = 50.0; //ESTABA EN 120
      myPID.Compute();

      if (input >= setpoint) {
        output = 0;
        Serial.println("Precalentamiento listo. Enfriando...");
        estadoActual = ENFRIANDO;
      }
      break;

    case ENFRIANDO:
      output = 0;
      if (input <= 40.0) { //ANTES EL VAOR ERA 70 PARA EL CAFE
        Serial.println("Temp ideal para carga. Envie 'T'");
        estadoActual = ESPERANDO_CONFIRMACION;
      }
      break;

    case ESPERANDO_CONFIRMACION:
      output = 0;
      Serial.println("Esperando Start...");
      // if (cmd == 'START') {
      //   setpoint = 50.0; //ESTABA 130
      //   windowStartTime = millis();
      //   motorStartMillis = millis();
      //   motorRunning = true;
      //   estadoActual = TUESTANDO;
      //   Serial.println("Iniciando tueste...");
      // }
      break;

    case TUESTANDO:
      if (millis() - windowStartTime >= 60000)  setpoint = 140.0;
      if (millis() - windowStartTime >= 120000) setpoint = 150.0;
      Serial.println("TUESTANDO EN PROCESO");
      myPID.Compute();
      break;

    case ERROR_TERMOPAR:
      digitalWrite(ssrPin, LOW);
      Serial.println("ERROR: Termopar no responde");
      while (true);
  }

  // ----------- PWM SSR -----------
  if (now - windowStartTime > windowSize) {
    windowStartTime += windowSize;
  }
  digitalWrite(ssrPin, (now - windowStartTime) < output);

  // ----------- MOTOR -----------
  if (motorRunning && motorRunTime > 0) {
    if (millis() - motorStartMillis >= motorRunTime) {
      motorController.TurnLeft(0);
      motorRunning = false;
      Serial.println("Motor detenido (tiempo cumplido)");
    } else {
      motorController.TurnLeft(22);
    }
  }

  // ----------- MONITOR SERIAL -----------
  Serial.print("Temp: ");
  Serial.print(input, 1);
  Serial.print(" °C | Estado: ");
  Serial.print(estadoActual);
  Serial.print(" | Set: ");
  Serial.print(setpoint);
  Serial.print(" | Motor: ");
  Serial.print(motorRunning ? "ON" : "OFF");
  actualizarTiempoRestante();
  printTime();   
  Serial.print(" | CMD: ");
  Serial.println(cmd);
  delay(200);
}