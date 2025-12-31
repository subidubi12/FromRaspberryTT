
import time
import serial  # Para leer del puerto serial
import math
import re
import threading

class LectorTermopar:
    def __init__(self, puerto='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_24238313635351910130-if00', baud=9600):
        self.arduino = serial.Serial(puerto,baud,timeout=1)
        self._temp = None
        self._estado = None
        self._setpoint = None
        self._motor = None
        self._running = False
        self._lock = threading.Lock()
    
    def iniciar(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._leer_serial,daemon=True)
        self._thread.start()
        
    def detener(self):
        self._running = False
        time.sleep(0.2)
        if self.arduino.is_open:
            self.arduino.close()
    
    def _leer_serial(self):
        print("comienza hilo")
        while self._running:
            linea = self.arduino.readline().decode('utf-8',errors='ignore').strip()
            print("RAW:", repr(linea))
            if not linea.startswith("Temp:"):
                continue
            match = re.search(r"Temp:\s*(-?\d+(?:\.\d+)?)", linea)
            if not match:
                continue
            
            temp = float(match.group(1))
            
            with self._lock:
                self._temp = temp
        
    def get_temperatura(self):
        with self._lock:
            return self._temp
    ####        MOTOR       ####
    def iniciar_control():
        
        if arduino.is_open:
          arduino.write(b"START\n")    
          print("enviado: START")

    def detener_control():
        if arduino.is_open:
            arduino.write(b"STOP\n")
            print("enviado: STOP")
        
    def send_command(cmd):
        #8, A, B, TIEMPO DEL MOTOR
        try:
            packet = f"{cmd}\n"
            arduino.write(packet.encode())
            print(f"comando enviado: {cmd}")
        except Exception as e:
            print("Error enviando comando:", e)

                
            
            
# # Puerto serial (ajústalo si es diferente)
# arduino = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
# #arduino = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
# time.sleep(2)

# # Variable para almacenar la temperatura
# temp_c = 0.0
    
# def read_temp():
    # global temp_c
    # if arduino.in_waiting > 0:
        # #linea = arduino.readline().decode('utf-8',errors='ignore').strip()
        # linea = arduino.readline().decode('utf-8',errors='ignore')
        # linea = linea.strip()
        # if not linea.startswith("Temp:"):#
            # return#
        # #print(f"Línea recibida: 'repr{linea}'")
        # print(len(linea), repr(linea))
        # #para saber con que se queda
        # match = re.search(r"Temp:\s*(-?\d+(?:\.\d+)?)", linea)
        # #print(f"match tiene:", match)
        # if match:
            # try:
                # temp_leida = float(match.group(1))  # solo el número antes del °C
                # print(f"Temperatura válida: {temp_leida}°C")
                # temp_c = temp_leida 
                # if math.isnan(temp_leida):
                    # print("⚠️ Es NaN, se descarta.")
                    # return None

                # temp_c = temp_leida
                # return temp_c

            # except ValueError:
                # print("❌ Error: No se pudo convertir el valor a float.")
                # return None
        # else:
            # print("⚠️ No se encontró temperatura en la línea.")
    # return None

# # Función para obtener el valor de la temperatura
# def get_temp():
    # return temp_c

# def iniciar_control():
    # if arduino.is_open:
        # arduino.write(b"START\n")    
        # print("enviado: START")

# def detener_control():
    # if arduino.is_open:
        # arduino.write(b"STOP\n")
        # print("enviado: STOP")
        
# def send_command(cmd):
    # #8, A, B, TIEMPO DEL MOTOR
    # try:
        # packet = f"{cmd}\n"
        # arduino.write(packet.encode())
        # print(f"comando enviado: {cmd}")
    # except Exception as e:
        # print("Error enviando comando:", e)

