
import time
import serial  # Para leer del puerto serial
import math
import re
import threading

class LectorTermopar:
    def __init__(self, puerto='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_24238313635351910130-if00', baud=9600):
        self.arduino = serial.Serial(puerto,baud,timeout=1)
        self._temp = None
        self._tiempo_restante = None
        self._etiquetaTiempo = None
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
            match_temperatura = re.search(r"Temp:\s*(-?\d+(?:\.\d+)?)", linea)
            match_tiempo = re.search(r"Tiempo Restante:\s*(\d+)m\s*(\d+)s", linea)
            if not match_temperatura: 
                continue
            
            temp = float(match_temperatura.group(1))
            
            if match_tiempo:
                minutos = int(match_tiempo.group(1))
                segundos = int(match_tiempo.group(2))
                tiempo_seg = minutos * 60 + segundos
                
            with self._lock:
                self._temp = temp
                self._tiempo_restante = tiempo_seg
                    
    def get_temperatura(self):
        with self._lock:
            return self._temp #ag etiqueta tiempo en declaracion y return
    
    def get_tiempo_restante(self):
        with self._lock:
            return self._tiempo_restante
    ####        MOTOR       ####
    def iniciar_control():
        
        if arduino.is_open:
          arduino.write(b"START\n")    
          print("enviado: START")

    def detener_control():
        if arduino.is_open:
            arduino.write(b"STOP\n")
            print("enviado: STOP")
        
    def send_command(self, cmd):
        #8, A, B, TIEMPO DEL MOTOR
        try:
            packet = f"{cmd}\n"
            self.arduino.write(packet.encode())
            print(f"comando enviado: {cmd}")
        except Exception as e:
            print("Error enviando comando:", e)

