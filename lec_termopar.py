""" #para termopar
import time
import board
import digitalio
import adafruit_max6675

# Configuración SPI
spi = board.SPI()  # Usa SPI por defecto: CLK=11, MISO=9, MOSI=10
cs = digitalio.DigitalInOut(board.D8)  # Chip select (CS) en GPIO8

# Crear el objeto del sensor
sensor = adafruit_max6675.MAX6675(spi, cs)

def termopar_lectura():
    try:
        while True:
            temp_c = sensor.temperature
            print(f"Temperatura: {temp_c:.2f} °C")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Lectura detenida.")

    return temp_c """
# termopar.py
# import time
# import random  # simula valores

# temp_c = 0.0

# def read_temp():
    # global temp_c
    # temp_c = random.uniform(20, 100)  # reemplaza con sensor.temperature
    # return temp_c

# def get_temp():
    # return temp_c
import time
import serial  # Para leer del puerto serial

# Puerto serial (ajústalo si es diferente)
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

# Variable para almacenar la temperatura
temp_c = 0.0

# Función para leer temperatura del puerto serial
def read_temp():
    global temp_c
    if arduino.in_waiting > 0:
        linea = arduino.readline().decode().strip()
        if linea.startswith("Temp:"):
            temp_c = float(linea.replace("Temp: ", ""))
    return temp_c

# Función para obtener el valor de la temperatura
def get_temp():
    return temp_c

# Bucle principal donde se lee la temperatura continuamente
#while True:
 #   read_temp()  # Lee la temperatura desde el puerto serial
  #  print(f"Temperatura: {get_temp()} °C")  # Muestra la temperatura
   # time.sleep(1)  # Espera 1 segundo antes de leer nuevamente
