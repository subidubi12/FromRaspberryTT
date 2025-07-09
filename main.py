import time
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from PIL import Image, ImageTk 
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.interpolate import interp1d
from numpy.polynomial import Polynomial
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.animation as animation 
import serial


from imagenes import rutas_imagenes,ruta_imagen_espera
from balanza import start_reading, stop_reading, reset_scale, ingreso_cafe, get_current_reading
#from lec_termopar import read_temp, get_temp
#from senzao import leer_serial
"""import RPi.GPIO as GPIO
from hx711 import HX711  # Asegúrate de tener instalada esta librería

# Configuración de GPIO y la balanza
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=2, pd_sck_pin=3)
hx.zero()"""


# Variable para controlar el bucle de lectura
running = False
tiempo_inicio = None
temperaturas = []
tiempos = []

# Puerto serial (ajústalo si es diferente)
#arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
#time.sleep(2)

def on_close():
    """Maneja el evento de cierre de la ventana."""
    stop_reading()
    #GPIO.cleanup()
    root.destroy()


class SlidePanel(ttk.Frame):
    def __init__(self, parent, start_pos, end_pos):
        super().__init__(master=parent,relief='solid',style='LIGHT')

        #atributos generales
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = abs(start_pos - end_pos)
        print(self.width)

        #place
        self.place(relx = self.start_pos, rely = 0, relwidth = self.width, relheight = 1)

# Función para cambiar la imagen según la selección
class PanelLateralDown(ttk.Frame):
    def __init__(self, parent, start_pos, end_pos):
        super().__init__(master=parent,relief='raised')

        #atributos generales
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = abs(start_pos - end_pos)
        print(self.width)

        #place
        self.place(relx = self.start_pos, rely = 0.5, relwidth = self.width, relheight = 0.5)

class NotebookFrame(ttk.Notebook):
    """Clase para el Notebook con dos pestañas."""
    def __init__(self, parent):
        super().__init__(master=parent)
        self.place(relx=0.3, rely=0, relwidth=0.7, relheight=1)

        # Crear pestañas
        self.create_tabs()

    def create_tabs(self):
        """Crea las pestañas del Notebook."""
        tab1 = tk.Frame(self, bg="lightblue", relief="groove", borderwidth=2)
        tab2 = tk.Frame(self, bg="lightgreen", relief="groove", borderwidth=2)
        tab3 = tk.Frame(self, bg="lightgreen", relief="groove", borderwidth=2)

        # Añadir pestañas
        self.add(tab1, text="Grafica Velocidad")
        self.add(tab2, text="Tiempo de espera")
        self.add(tab3, text="Temperatura Real Prueba")

        # --- Gráfica para la primera pestaña ---
        fig1, ax = plt.subplots()
        canvas1 = FigureCanvasTkAgg(fig1, master=tab1)

        fig1 = Figure(figsize=(5, 4), dpi=100)
        tiempo = np.array([0, 30, 50, 90, 120, 180, 240, 300, 360, 420, 480, 540, 600])
        temperature_celsius = np.array([214, 103, 75, 84, 94, 105, 127, 138, 150, 165, 180, 195, 200])

        time_dense = np.linspace(tiempo.min(), tiempo.max(), 500)
        interp_func = interp1d(tiempo, temperature_celsius, kind='cubic')
        temperature_smooth = interp_func(time_dense)

        # Ajuste polinomial en los puntos finales
        adjusted_time = np.array([360, 420, 480, 540, 600])
        adjusted_temperature = np.array([150, 165, 180, 195, 200])
        time_final = np.concatenate((time_dense[-50:], adjusted_time))
        temperature_final = np.concatenate((temperature_smooth[-50:], adjusted_temperature))
        # Polinomio de segundo grado
        p = Polynomial.fit(time_final, temperature_final, 2)
        temperature_smooth[-50:] = p(time_dense[-50:])
        # Gráfica
        ax.plot(time_dense, temperature_smooth, 'g-', linewidth=1.5, label='Tostado suave')
        ax.scatter([0, 90, 360, 540, 600], [214, 84, 150, 195, 200], color='red', label='Puntos clave')
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Temperatura (°C)')
        ax.set_title('Curva de tueste del perfil Suave')
        ax.set_xlim(0, 600)
        ax.grid(True)
        ax.legend(loc='best', frameon=False)

        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=0)

        # --- Gráfica para la segunda pestaña ---
        fig2 = Figure(figsize=(5, 4), dpi=100)
        ax2 = fig2.add_subplot(111)
        t = np.arange(0, 5, 0.1)
        ax2.plot(t, t**2, 'r-', label="Tiempo de espera")
        ax2.set_title("Tiempo de Espera")
        ax2.legend()
        canvas2 = FigureCanvasTkAgg(fig2, master=tab2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=0)

        def configurar_graficaTemperatura(tab3):
            global fig3, ax3, canvas3, trayectoria, tiempo_inicio

            tiempo_inicio = time.time()
            fig3 = Figure(figsize=(5, 4), dpi=100)
            ax3=fig3.add_subplot(111)
            ax3.set_title("Temperatura en tiempo real")
            ax3.set_xlabel("Tiempo (s)")
            ax3.set_ylabel("Temperatura (°C)")
            ax3.grid(True)
            

            trayectoria, = ax3.plot([],[],'b-') #en los corchetes va la gráfica

            canvas3 = FigureCanvasTkAgg(fig3, master=tab3)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=0)

        def actualizar_temperatura(): #trae el valor de la temperatura
            read_temp()
            temperatura = get_temp()
            #leer_serial()
            valorTemperatura.config(text=f"{temperatura:.2f} °C") #se imprime el valor de la temperatura
            tiempo_actual = time.time() - tiempo_inicio
            temperaturas.append(temperatura)
            tiempos.append(tiempo_actual)

            trayectoria.set_data(tiempos,temperaturas)
            # Ajustar los límites del eje y (de 0 a 220 grados)
            #ax3.set_ylim(0, 220)

            # Ajustar los límites del eje x (de 0 a 10 minutos)
            #ax3.set_xlim(0, 10)

            ax3.relim()
            ax3.autoscale_view()
            canvas3.draw()
            tab3.after(10000, actualizar_temperatura)  # se actualiza cada 1 segundo, y va agregando los datos 


        # Widget
        valorTemperatura = ttk.Label(master=tab3, text="-- °C", bootstyle='INFO')
        valorTemperatura.pack()
        configurar_graficaTemperatura(tab3)
        #actualizar_temperatura() #se manda a llamar a la función que actualiza el valor de la temperatura
        

#TTK Boostrap
root = ttk.Window(themename = 'lumen')

root.title("Lectura de Peso")
root.geometry("1200x600")
root.protocol("WM_DELETE_WINDOW", on_close)

panelLateral = SlidePanel(root,0,0.3)

#panellateralDown = PanelLateralDown(root, 0, 0.3)

imagenes_mini = {}  # Para guardar referencias
imagenes_grandes = {}

notebook = NotebookFrame(root)

# Contenedor horizontal de miniaturas
frame_miniaturas = tk.Frame(panelLateral) #contenedor con los modos de tueste

for nombre, ruta in rutas_imagenes.items():
    # Cargar imagen miniatura
    img = Image.open(ruta).resize((80, 80))
    img_tk = ImageTk.PhotoImage(img)
    imagenes_mini[nombre] = img_tk
    #Carga imagen de WAIT
    img_espera = Image.open(ruta_imagen_espera).resize((300, 300))
    img_espera_tk = ImageTk.PhotoImage(img_espera)

    # Cargar imagen grande para seleccionar
    img_grande = Image.open(ruta).resize((250, 250))
    img_grande_tk = ImageTk.PhotoImage(img_grande)
    imagenes_grandes[nombre] = img_grande_tk

    # Botón con imagen
    btn = tk.Button(frame_miniaturas, image=img_tk,
                    command=lambda n=nombre: actualizar_tueste(n))
    btn.pack(side=tk.LEFT, padx=5)

def actualizar_tueste(nombre):
    label_tueste.config(text=f"{nombre}", font=("Arial", 14))
    label_imagen_grande.config(image=img_espera_tk)
    label_imagen_grande.image = img_espera_tk 

    label_imagen_grande.config(image=imagenes_grandes[nombre])
    label_imagen_grande.image = imagenes_grandes[nombre]  # mantener referencia 

    print(nombre)

#Etiqueta que cambia
label_tueste = tk.Label(panelLateral, text="Selecciona un tueste", font=("Arial", 14), justify="left")
label_tueste.pack(pady=10)
# Imagen grande
label_imagen_grande = tk.Label(panelLateral,bd=2,fg="gray",relief="groove")
label_imagen_grande.pack(pady=10)

frame_botones = tk.Frame(panelLateral) #contenedor con los modos de tueste

btn_inicio = tk.Button(frame_botones, text="Inicio", font=("Arial", 14), height=5, width=10,borderwidth=0)
btn_inicio.pack(pady=10,padx=10, side=tk.LEFT,)

btn_pausa = tk.Button(frame_botones, text="Pausa", font=("Arial", 14), height=5, width=10,borderwidth=0)
btn_pausa.pack(pady=10,padx=10,side=tk.LEFT)

#Tueste del frame
label_seleccionaTueste = tk.Label(panelLateral, text="Selecciona tu tueste", font=("Arial", 8))
label_seleccionaTueste.pack(anchor="nw",pady=10,padx=10)
frame_miniaturas.pack(pady=10)

frame_botones.pack(pady=10)

#Se manda llamar al termopar
#termopar_lectura()
# Etiqueta para mostrar el peso
weight_label = ttk.Label(panelLateral, text="Peso: --", font=("Arial", 18))
weight_label.pack(pady=20)

start_button = ttk.Button(panelLateral, text="Iniciar", width=10,  command=lambda: start_reading(weight_label), bootstyle='SUCCESS')
start_button.pack(side=ttk.LEFT, padx = 5)#grid(row=0, column=0, padx=10)

stop_button = ttk.Button(panelLateral, text="Detener", width=10, command=lambda:stop_reading,bootstyle='DANGER')
stop_button.pack(side=ttk.RIGHT, padx = 5)#grid(row=0, column=1, padx=10)

reset_button = ttk.Button(panelLateral, text="Reiniciar", width=10, command=lambda:reset_scale(weight_label),bootstyle='PRIMARY')
reset_button.pack(side=ttk.BOTTOM, pady = 20)#grid(row=1, column=0, columnspan=2, pady=10)

ingresar_button = ttk.Button(panelLateral, text="Ingresar Cafe", width=10, command=lambda:ingreso_cafe(get_current_reading()),bootstyle='SUCCESS')
ingresar_button.pack(side=ttk.BOTTOM, pady = 20)#grid(row=1, column=0, columnspan=2, pady=10)

# Iniciar la aplicación
root.mainloop()
