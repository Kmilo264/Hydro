import os
import sys
import numpy as np

from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from datetime import datetime

import pyqtgraph as pg

import time
import serial

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

gui_class = uic.loadUiType("gui/main.ui")[0]

DATOS = 8

class NewList():

    def __init__(self, max):
        self.l = []
        self.max = max

    def append(self, element):
        if len(self.l) == self.max:
            self.l.pop(0)
        self.l.append(element)


class Gui(QMainWindow, gui_class):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.n = 0

        self.puerto = ""
        self.baudrate = 9600

        self.cant_acel1 = 100
        self.cant_acel2 = 100
        self.cant_vel = 400


        self.acel_x1_all = NewList(self.cant_acel1)
        self.acel_y1_all = NewList(self.cant_acel1)
        self.acel_z1_all = NewList(self.cant_acel1)
        
        self.acel_x2_all = NewList(self.cant_acel2)
        self.acel_y2_all = NewList(self.cant_acel2)
        self.acel_z2_all = NewList(self.cant_acel2)
        self.velocidad_all = NewList(self.cant_vel)

        self.pg_window_acel1 = pg.GraphicsWindow()
        self.pg_window_acel2 = pg.GraphicsWindow()

        self.pg_window_vel = pg.GraphicsWindow()


        self.pg_gen_acel1 = self.pg_window_acel1.addPlot()
        self.pg_gen_acel1.addLegend()
        self.pg_plot_acel1_x = self.pg_gen_acel1.plot(name="eje x")
        self.pg_plot_acel1_y = self.pg_gen_acel1.plot(name="eje y")
        self.pg_plot_acel1_z = self.pg_gen_acel1.plot(name="eje z")

        self.pg_gen_acel2 = self.pg_window_acel2.addPlot()
        self.pg_gen_acel2.addLegend()
        self.pg_plot_acel2_x = self.pg_gen_acel2.plot(name="eje x")
        self.pg_plot_acel2_y = self.pg_gen_acel2.plot(name="eje y")
        self.pg_plot_acel2_z = self.pg_gen_acel2.plot(name="eje z")

        self.pg_gen_vel = self.pg_window_vel.addPlot()
        self.pg_plot_vel = self.pg_gen_vel.plot()

        self.qt_aceleracion_layout.addWidget(self.pg_window_acel1)
        self.qt_velocidad_layout.addWidget(self.pg_window_vel)
        self.qt_aceleracion2_layout.addWidget(self.pg_window_acel2)

        self.qt_conectar_button.clicked.connect(self.conectar)
        self.qt_parar_button.clicked.connect(self.parar)
        self.qt_guardar_button.clicked.connect(self.guardar)
        self.qt_limpiar_button.clicked.connect(self.limpiar)

        # Inclinacion
        self.label = QtWidgets.QLabel(
            "<---------------->",
            alignment=QtCore.Qt.AlignCenter
            )
        
        graphicsview = QtWidgets.QGraphicsView()
        scene = QtWidgets.QGraphicsScene(graphicsview)
        graphicsview.setScene(scene)

        self.proxy = QtWidgets.QGraphicsProxyWidget()
        self.proxy.setWidget(self.label)
        self.proxy.setTransformOriginPoint(self.proxy.boundingRect().center())
        scene.addItem(self.proxy)

        self.qt_inclinacion_layout.addWidget(graphicsview)


    def read_data(self, buffer):
        l_buffer = len(buffer.split("*"))

        if not l_buffer == DATOS:
            return
        try:
            splitted = buffer.split("*")
            x1 = float(splitted[0])
            y1 = float(splitted[1])
            z1 = float(splitted[2])
            
            x2 = float(splitted[3])
            y2 = float(splitted[4])
            z2 = float(splitted[5])

            theta = float(splitted[6])
            v = float(splitted[7])
            
            self.proxy.setRotation(theta)
        except:
            print("Error convirtiendo a numero")
            return
        self.n += 1

        self.acel_x1_all.append(x1)
        self.acel_z1_all.append(z1)
        self.acel_y1_all.append(y1)
        
        self.acel_x2_all.append(x2)
        self.acel_y2_all.append(y2)
        self.acel_z2_all.append(z2)

        self.velocidad_all.append(v)

        self.pg_plot_acel1_x.setData(
            self.acel_x1_all.l,
            pen=(1, 3),
            antialias=True,
        )

        self.pg_plot_acel1_y.setData(
            self.acel_y1_all.l,
            pen=(2, 3),
            antialias=True,
        )

        self.pg_plot_acel1_z.setData(
            self.acel_z1_all.l,
            pen=(3, 3),
            antialias=True,
        )

        self.pg_plot_acel2_x.setData(
            self.acel_x2_all.l,
            pen=(1, 3),
            antialias=True,
        )

        self.pg_plot_acel2_y.setData(
            self.acel_y2_all.l,
            pen=(2, 3),
            antialias=True,
        )

        self.pg_plot_acel2_z.setData(
            self.acel_z2_all.l,
            pen=(3, 3),
            antialias=True,
        )

        self.pg_plot_vel.setData(
            self.velocidad_all.l,
            antialias=True,
            pen=pg.mkPen(color=(255, 100, 100))
        )

        self.qt_velocidad_lcd.display(v)
        self.statusBar().showMessage("{0} datos".format(self.n))

    
    def conectar(self):
        puerto = str(self.qt_puerto_lineedit.text())
        baudrate = str(self.qt_velocidad_lineedit.text())
        
        if puerto and baudrate.isdigit():
            baudrate = int(baudrate)
            print("conectando a: {0}:{1}".format(puerto, baudrate))
            self.st = SerialThread(puerto, baudrate)
            self.st.signal.connect(self.read_data)
            self.st.start()
    
    def guardar(self):
        print("Guardar")
    
    def parar(self):
        print("parar")
        self.st.terminate()
    
    def limpiar(self):

        self.acel_x1_all = NewList(self.cant_acel1)
        self.acel_y1_all = NewList(self.cant_acel1)
        self.acel_z1_all = NewList(self.cant_acel1)
        
        self.acel_x2_all = NewList(self.cant_acel2)
        self.acel_y2_all = NewList(self.cant_acel2)
        self.acel_z2_all = NewList(self.cant_acel2)
        self.velocidad_all = NewList(self.cant_vel)
        self.n = 0

        self.pg_plot_acel1_x.clear()
        self.pg_plot_acel1_y.clear()
        self.pg_plot_acel1_z.clear()

        self.pg_plot_acel2_x.clear()
        self.pg_plot_acel2_y.clear()
        self.pg_plot_acel2_z.clear()

        self.pg_plot_vel.clear()

        self.qt_velocidad_lcd.display(0)
        self.proxy.setRotation(0)


class SerialThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, puerto, baudrate):
        QThread.__init__(self)
        self.puerto = puerto
        self.velocidad = baudrate
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(
            self.puerto,
            self.velocidad
        )
    
    def guardar(self, buffer):
        with open("data.txt", "a+") as f:
            f.write(buffer.replace("*", ","))
            f.write("\r\n")

    def run(self):
        self.connect()
        buffer = ""
        self.guardar("")
        self.guardar(str(datetime.today()))
        self.guardar("")
        while True:
            try:
                byte = self.ser.read(1).decode("utf8")
                if byte == "\n":
                    buffer = buffer.strip()
                    self.signal.emit(buffer)
                    if len(buffer.split("*")) == DATOS:
                        self.guardar(buffer)
                    else:
                        print("No suficientes datos")
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
