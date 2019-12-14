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

        self.acel_x_all = []
        self.acel_y_all = []
        self.acel_z_all = []


        self.pg_window_acel = pg.GraphicsWindow()
        self.pg_window_vel = pg.GraphicsWindow()

        self.pg_plot_acel_x = self.pg_window_acel.addPlot()
        self.pg_plot_acel_y = self.pg_window_acel.addPlot()

        self.pg_plot_vel = self.pg_window_vel.addPlot()

        self.qt_aceleracion_layout.addWidget(self.pg_window_acel)
        self.qt_velocidad_layout.addWidget(self.pg_window_vel)

        self.qt_conectar_button.clicked.connect(self.conectar)
        self.qt_parar_button.clicked.connect(self.parar)
        self.qt_guardar_button.clicked.connect(self.guardar)
        self.qt_limpiar_button.clicked.connect(self.limpiar)

    
    def read_data(self, buffer):
        
        d = -1000

        l_buffer = len(buffer.split("*"))

        if not l_buffer >= 3:
            return
        try:
            x = float(buffer.split("*")[1])
            y = float(buffer.split("*")[2])
        except:
            print("Error convirtiendo a numero")
            return
        x = self.n
        self.n += 1

        print("ploting", x, y, d)

        self.acel_x_all.append(x)
        self.acel_z_all.append(y+ 300)
        self.acel_y_all.append(y)

        self.pg_plot_acel_x.clear()
        self.pg_plot_acel_y.clear()
        self.pg_plot_vel.clear()

        a = self.pg_plot_acel_x.plot(title="Acelerometro 1")
        self.pg_plot_acel_x.addLegend()
        self.pg_plot_acel_x.plot(
            self.acel_x_all[d:],
            self.acel_y_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 100, 100)),
            pen=(1, 2),
            antialias = True,
            name="adfg"
        )

        self.pg_plot_acel_x.plot(
            self.acel_x_all[d:],
            self.acel_z_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            # pen=pg.mkPen(color=(255, 255, 255)),
            pen=(2,2),
            antialias = True,
            name="f"
        )

        self.pg_plot_acel_y.plot(
            self.acel_x_all[d:],
            self.acel_y_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            pen=pg.mkPen(color=(255, 100, 100)),
            antialias = True
        )

        self.pg_plot_vel.plot(
            self.acel_x_all[d:],
            self.acel_y_all[d:],
            #symbol="o",
            style=QtCore.Qt.DotLine,
            pen=pg.mkPen(color=(255, 100, 100)),
            antialias = True
        )
    
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
        print("limpiar")

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
                if byte == ";":
                    self.signal.emit(buffer)
                    self.guardar(buffer)
                    time.sleep(0.1)
                    buffer = ""
                else:
                    buffer += byte
            except:
                pass

app = QApplication(sys.argv)
corel = Gui(None)
corel.show()
app.exec_()
