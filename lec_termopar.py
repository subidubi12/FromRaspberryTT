
import time
import serial  # Para leer del puerto serial
import math
import re
# Puerto serial (ajústalo si es diferente)
#arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
arduino = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
time.sleep(2)

# Variable para almacenar la temperatura
temp_c = 0.0

# Función para leer temperatura del puerto serial
# ~ def read_temp():
    # ~ global temp_c
    # ~ if arduino.in_waiting > 0:
        # ~ linea = arduino.readline().decode(errors='ignore').strip()
        # ~ if linea.startswith("Temp:"):
            # ~ try:
                # ~ print(linea)
                
                # ~ temp_c = float(linea.replace("Temp:", "").strip())
            # ~ except ValueError:
                # ~ print("Error: No se pudo convertir la temperatura a float.")
    # ~ return temp_c


# def read_temp():
    # global temp_c
    # if arduino.in_waiting > 0:
        # linea = arduino.readline().decode(errors='ignore').strip()
        # print(f"Línea recibida: '{linea}'") 
        # if linea.startswith("Temp: "):
            # try:
                # print(linea)
                # valor_str = linea.replace("Temp: ", "").strip().replace("C", "")
                # temp_leida = float(valor_str)
                # print(temp_leida)

                # # Validamos si el valor es numérico y no es NaN
                # if math.isnan(temp_leida):
                    # print("⚠️ Dato recibido es NaN. Se descarta.")
                    # return None

                # temp_c = temp_leida
                # return temp_c

            # except ValueError:
                # print(" Error: No se pudo convertir la temperatura a float.")
                # return None
    # return None
    
def read_temp():
    global temp_c
    if arduino.in_waiting > 0:
        linea = arduino.readline().decode(errors='ignore').strip()
        print(f"Línea recibida: '{linea}'")

        match = re.search(r"Temp:\s*(-?\d+(\.\d+)?)°C", linea)
        if match:
            try:
                temp_leida = float(match.group(1))  # solo el número antes del °C
                print(f"Temperatura válida: {temp_leida}°C")

                if math.isnan(temp_leida):
                    print("⚠️ Es NaN, se descarta.")
                    return None

                temp_c = temp_leida
                return temp_c

            except ValueError:
                print("❌ Error: No se pudo convertir el valor a float.")
                return None
        else:
            print("⚠️ No se encontró temperatura en la línea.")
    return None

# Función para obtener el valor de la temperatura
def get_temp():
    return temp_c

def iniciar_control():
    if arduino.is_open:
        arduino.write(b"START\n")    
        print("enviado: START")

def detener_control():
    if arduino.is_open:
        arduino.write(b"STOP\n")
        print("enviado: STOP")

