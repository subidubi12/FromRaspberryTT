
import time
import serial  # Para leer del puerto serial
import math
import re
import threading

class LectorTermopar:
    def __init__(self, puerto='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_24238313635351910130-if00', baud=9600):
        self.arduino = serial.Serial(puerto,baud,timeout=1)
        self._temp = None
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
            match = re.search(r"Temp:\s*(-?\d+(?:\.\d+)?)", linea)
            matchTiempo = re.search(r"Tiempo Restante:\s*(\d+)m?\s*(\d+)s", linea)
            if not match #|| matchTiempo: #se agrego || matchTirempo
                continue
            
            temp = float(match.group(1))
            
            with self._lock:
                self._temp = temp
        
    def get_temperatura(self):
        with self._lock:
            return self._temp #ag etiqueta tiempo en declaracion y return
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
            self.arduino.write(packet.encode())
            print(f"comando enviado: {cmd}")
        except Exception as e:
            print("Error enviando comando:", e)

