import tkinter as tk
import serial
import threading
import time


# Puerto serial (ajústalo si es diferente)
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)
# Función para leer serial en segundo plano
def leer_serial():
    while True:
        if arduino.in_waiting > 0:
            linea = arduino.readline().decode().strip()
            if linea.startswith("Temp:"):
                temperatura = linea.replace("Temp: ", "")
                temp_label.config(text=f"Temperatura: {temperatura} °C")
                
#FUNCION PARA ENVIAR A TRAVES DEL SERIAL 
def send_command(self,cmd):
    #8, A, B, TIEMPO DEL MOTOR
    try:
        packet = f"{cmd}\n"
        arduino.write(packet.encode())
        #print(f"comando enviado: {cmd}")
    except Exception as e:
        print("Error enviando comando:", e)
        
                        
                
# # GUI con Tkinter
root = tk.Tk()
root.title("Monitor de Temperatura")
root.geometry("300x150")

temp_label = tk.Label(root, text="Temperatura: -- °C", font=("Arial", 16))
temp_label.pack(pady=40)

# # Hilo para leer datos sin congelar la interfaz
hilo = threading.Thread(target=leer_serial, daemon=True)
hilo.start()

root.mainloop()
