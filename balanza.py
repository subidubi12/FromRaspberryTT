import time
from tkinter import messagebox
import threading

reading = 0.0  # fuera de funciones

def get_current_reading():
    return reading

def start_reading(weight_label):
    global running
    running = True
    threading.Thread(target=read_weight, args=(weight_label,), daemon=True).start()


def stop_reading():
    """Detiene la lectura del peso."""
    global running
    running = False

def reset_scale(weight_label):
    """Resetea la balanza a cero."""
    #hx.zero()
    weight_label.config(text="Peso: 0.00")
    weight_label.config(fg="black")
    return weight_label

def read_weight(weight_label):
    """Lee el peso de la balanza y actualiza la etiqueta."""
    global reading
    while running:
        try:
            reading = 0.90#hx.get_data_mean(10)
            if reading is not None:
                # Actualiza el texto con el peso y cambia el color
                weight_label.config(text=f"Peso: {reading:.2f} kg")
                if reading < 0:  # Evitar lecturas negativas
                    weight_label.config(fg="red")
                else:
                    weight_label.config(fg="green")
            else:
                weight_label.config(text="Peso: Error de lectura", fg="red")
            time.sleep(0.5)
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error: {e}")
            stop_reading()

def ingreso_cafe(reading):
    #cambiar por la variable que 
    #reading = 1.2
    if reading < 0.15:
        messagebox.showerror('Ingreso de café', f"El peso actual del café es de: {reading} Kg, Por favor ingrese más café" )
    elif reading > 0.15 and reading < 1.1:
        respuesta = messagebox.askokcancel('Ingreso de café', f"El peso actual del café es de: {reading} Kg, ¿seguro que quiere ingresarlo?")        
    elif reading > 1.1:
        messagebox.showerror('Ingreso de café', f"El peso actual del café es de: {reading} Kg, por favor retire café")
    return reading, respuesta
