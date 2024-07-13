import serial
import pyodbc
import threading
from datetime import datetime
import tkinter as tk
from tkinter import Label, Button

#Porta serial
serial_port = 'COM4'
baud_rate = 9600

#SQL Server
server = 'x'
database = 'x'
username = 'x'
password = 'x'

class SensorDataApp:
    def __init__(self, master):
        self.master = master
        master.title("IRRIAGRO")
        
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        window_width = int(screen_width * 0.2)
        window_height = int(screen_height * 0.2)
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        master.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

        self.label = Label(master, text="Status: Aguardando comando")
        self.label.pack()

        self.start_button = Button(master, text="Iniciar", command=self.start_reading, width=15, height=2)
        self.start_button.pack(pady=5)

        self.stop_button = Button(master, text="Parar", command=self.stop_reading, width=15, height=2)
        self.stop_button.pack(pady=5)

        self.running = False
        self.thread = None

    def start_reading(self):
        if not self.running:
            self.running = True
            self.label.config(text="Status: Conectando ao banco de dados...")
            self.thread = threading.Thread(target=self.read_sensor_data)
            self.thread.start()

    def stop_reading(self):
        self.running = False
        self.label.config(text="Status: Parado")

    def read_sensor_data(self):
        try:
            conn = pyodbc.connect(
                'DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
            )
            self.label.config(text="Status: Banco de dados conectado")
            ser = serial.Serial(serial_port, baud_rate)
            self.label.config(text="Status: Porta serial aberta")

            while self.running:
                line_temp = ser.readline().decode().strip()
                if 'Temperatura:' not in line_temp:
                    continue
                Temperature = float(line_temp.split(':')[1].strip().split('°')[0])

                line_humidity = ser.readline().decode().strip()
                if 'Umidade do Solo:' not in line_humidity:
                    continue
                Humidity_sensor_value = float(line_humidity.split(':')[1].strip())
                
                Humidity_percent = (1 - (Humidity_sensor_value / 1000)) * 100

                ReadingTime = datetime.now()

                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO DadosSensores (SESO_ID, DDSE_ValorMetrica, DDSE_DataExecucao) VALUES (?, ?, ?)", (4, Temperature, ReadingTime))
                    cursor.execute("INSERT INTO DadosSensores (SESO_ID, DDSE_ValorMetrica, DDSE_DataExecucao) VALUES (?, ?, ?)", (3, Humidity_percent, ReadingTime))
                    conn.commit()
                    self.label.config(text=f"Dados inseridos: Temp={Temperature}°C, Umidade={Humidity_percent}%")
                except pyodbc.Error as e:
                    self.label.config(text=f"Erro ao inserir dados: {e}")
                finally:
                    cursor.close()
        finally:
            conn.close()
            self.label.config(text="Status: Conexão com o banco de dados fechada")

def main():
    root = tk.Tk()
    app = SensorDataApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
