import os
import sys
import numpy as np

from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

import pyqtgraph as pg

import time
import serial

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

gui_class = uic.loadUiType("gui/main.ui")[0]

class Gui(QMainWindow, gui_class):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.n = 0

        self.acel_x1_all = []
        self.acel_y1_all = []
        self.acel_z1_all = []
        
        self.acel_x2_all = []
        self.acel_y2_all = []
        self.acel_z2_all = []
        self.velocidad_all = []

        self.pg_window_acel = pg.GraphicsWindow()
        self.pg_window_acel2 = pg.GraphicsWindow()

        self.pg_window_vel = pg.GraphicsWindow()

        self.pg_plot_acel_x = self.pg_window_acel.addPlot()
        self.pg_plot_acel_y = self.pg_window_acel2.addPlot()

        self.pg_plot_vel = self.pg_window_vel.addPlot()

        self.qt_aceleracion_layout.addWidget(self.pg_window_acel)
        self.qt_velocidad_layout.addWidget(self.pg_window_vel)
        self.qt_aceleracion2_layout.addWidget(self.pg_window_acel2)

        self.qt_conectar_button.clicked.connect(self.conectar)
        self.qt_parar_button.clicked.connect(self.parar)
        self.qt_guardar_button.clicked.connect(self.guardar)
        self.qt_limpiar_button.clicked.connect(self.limpiar)

    
    def read_data(self, buffer):
        
        d = -100

        l_buffer = len(buffer.split("*"))

        if not l_buffer >= 7:
            return
        try:
            splitted = buffer.split("*")
            x1 = float(splitted[0])
            y1 = float(splitted[1])
            z1 = float(splitted[2])
            
            x2 = float(splitted[3])
            y2 = float(splitted[4])
            z2 = float(splitted[5])

            v = float(splitted[6])
        except:
            print("Error convirtiendo a numero")
            return
        x = self.n
        self.n += 1

        self.acel_x1_all.append(x1)
        self.acel_z1_all.append(z1)
        self.acel_y1_all.append(y1)
        
        self.acel_x2_all.append(x2)
        self.acel_y2_all.append(y2)
        self.acel_z2_all.append(z2)
        self.velocidad_all.append(v)
        
        

        self.pg_plot_acel_x.clear()
        self.pg_plot_acel_y.clear()
        self.pg_plot_vel.clear()

        self.pg_plot_acel_x.addLegend()
        self.pg_plot_acel_x.plot(
            range(self.n)[d:],
            self.acel_x1_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 100, 100)),
            pen=(1, 3),
            antialias = True,
            name="eje x"
        )
        
        
        self.pg_plot_acel_x.plot(
            range(self.n)[d:],
            self.acel_y1_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 100, 100)),
            pen=(2, 3),
            antialias = True,
            name="eje y"
        )
        
        self.pg_plot_acel_x.plot(
            range(self.n)[d:],
            self.acel_z1_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 100, 100)),
            pen=(3, 3),
            antialias = True,
            name="eje z"
        )



        self.pg_plot_acel_y.addLegend()
        self.pg_plot_acel_y.plot(
            range(self.n)[d:],
            self.acel_x2_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 100, 100)),
            pen=(1, 3),
            antialias = True,
            name="eje x"
        )
        
        
        self.pg_plot_acel_y.plot(
            range(self.n)[d:],
            self.acel_y2_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 100, 100)),
            pen=(2, 3),
            antialias = True,
            name="eje y"
        )
        
        self.pg_plot_acel_y.plot(
            range(self.n)[d:],
            self.acel_z2_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 100, 100)),
            pen=(3, 3),
            antialias = True,
            name="eje z"
        )

        self.pg_plot_vel.plot(
           range(self.n)[d:],
           self.velocidad_all[d:],
           #symbol="o",
           style=QtCore.Qt.DotLine,
           pen=pg.mkPen(color=(255, 100, 100)),
           antialias = True
       )

        self.qt_velocidad_lcd.display(v)
    
    def conectar(self):
        puerto = str(self.qt_puerto_lineedit.text())
        
        if puerto:
            print(puerto)
            self.st = SerialThread(puerto)
            self.st.signal.connect(self.read_data)
            self.st.start()
    
    def guardar(self):
        print("Guardar")
    
    def parar(self):
        print("parar")
        self.st.terminate()
    
    def limpiar(self):
        self.acel_x1_all = []
        self.acel_x2_all = []
        self.acel_y1_all = []
        self.acel_y2_all = []
        self.acel_z1_all = []
        self.acel_z2_all = []
        self.velocidad_all = []
        self.n = 0
        self.pg_plot_acel_x.clear()
        self.pg_plot_acel_y.clear()
        self.pg_plot_vel.clear()


class SerialThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, puerto):
        QThread.__init__(self)
        self.puerto = puerto
        self.velocidad = 9600
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(
            self.puerto,
            self.velocidad
        )
    
    def guardar(self, buffer):
        with open("data.txt", "a+") as f:
            f.write(buffer)

    def run(self):
        self.connect()
        buffer = ""
        while True:
            try:
                byte = self.ser.read(1).decode("utf8")
                if byte == "\n":
                    self.signal.emit(buffer)
                    self.guardar(buffer)
                    time.sleep(0.1)
                    print(buffer)
                    buffer = ""
                else:
                    buffer += byte
            except Exception as e:
                print(e)
                buffer = ""

app = QApplication(sys.argv)
corel = Gui(None)
corel.show()
app.exec_()
