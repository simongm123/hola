# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""
#librerias de pyQt
#librerias encargadas de recibir y morstrar informacion al usuario.
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from PyQt5.uic import loadUi
#from matplotlib.figure import Figure
import scipy.io as sio
import numpy as np

class VentanaGrafica(QMainWindow):
    def __init__(self):
        #llamamos al constructor de la clase padre
        super(VentanaGrafica,self).__init__();
        #donde se carga el archivo designer
        loadUi('VisualizarSeñal.ui',self);
        #metodo auxilar configurar lo que queremos que "haga" la interfaz
        self.setup();
        #creamos una variable donde se encontrara la informacion a exportar
        self.__guardar=np.asarray([])
    
    
    def setup(self):
       
        #se organizan las conecciones de los botones 
        self.Boton_carga.clicked.connect(self.opcion_cargar)
#        self.adelantesenal.clicked.connect(self.adelante_senal)
#        self.atrassenal.clicked.connect(self.atrasar_senal)
        self.Boton_graficar.clicked.connect(self.opcion_graficar)
        self.Boton_filtrar.clicked.connect(self.opcion_filtro)
        self.Boton_guarda.clicked.connect(self.opcion_guardar)
#     
#        #hay botones que no deberian estar habilitados si no he cargado la senal 
        self.adelantesenal.setEnabled(False)
        self.atrassenal.setEnabled(False)
        self.Boton_graficar.setEnabled(False)
        self.Boton_filtrar.setEnabled(False)
        self.Boton_guarda.setEnabled(False)
#    
#   
        
        
    def opcion_graficar(self):#realiza la funcion de leer el canal que quiere viualizar 
        canal= int(self.Seleccioncanal.text())
        datos= self.__mi_controlador.devolver_canal(canal, self.__x_min, self.__x_max)#envia la informacion de canal a modelo y recibe la señal del canal que el usuario ingreso
        print("Variable python: " + str(type(datos)));
        print("Tipo de variable cargada: " + str(datos.dtype));
        print("Dimensiones de los datos cargados: " + str(datos.shape));
        print("Número de dimensiones: " + str(datos.shape[0]));
        print("Tamaño: " + str(datos.size));
        print("Tamaño de memoria (bytes): " + str(datos.nbytes));
        self.graficar_senal(datos) #envio la señal con unico canal a graficar mediante la funcion graficar senal
        
    def opcion_cargar(self):#funcion encargada de cargar los datos que ingresara el usuario
        #se abre el cuadro de dialogo para cargar
        #* son archivos .mat
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir senal","","Todos los archivos (*);;Archivos mat (*.mat)*")
        if archivo != "":
            print(archivo)
            #la senal carga exitosamente entonces habilito los botones
            datamat = sio.loadmat(archivo)
            data = datamat["data"]#guardo en data el archivo con la informacion correspondiente a los sensores y numero de muestras y etapas 
            #volver continuos los datos
            sensores,puntos,ensayos=data.shape
            senal_continua=np.reshape(data,(sensores,puntos*ensayos),order="F")
#            #el coordinador recibe y guarda la senal en su propio .py, por eso no 
#            #necesito una variable que lo guarde en el .py interfaz
#            self.__coordinador.recibirDatosSenal(senal_continua)
            self.__x_min=0
            self.__x_max=(data.shape[1])
            self.__mi_dimension=(data.shape[0])#ingreso a mi variable la dimension maxima de las graficas
            self.Seleccioncanal.setMinimum(0)
            self.Seleccioncanal.setMaximum((int(self.__mi_dimension))-1)#limito mi seleccionador con el numero maximo de chanels
            #habilito los botones que anteriormente tenia desactivados
            self.adelantesenal.setEnabled(True)
            self.atrassenal.setEnabled(True)
            self.Boton_graficar.setEnabled(True)
            self.Boton_filtrar.setEnabled(True)
            #asigno los datos al modelo
            self.__mi_controlador.asignarDatos(senal_continua)
            datos=self.__mi_controlador.devolver_segmento(self.__x_min,self.__x_max)
            
            
            self.graficar_senal(datos)#grafico todos los canales inicialmente mediante la funcion graficar senal
#            
    def graficar_senal(self,senal):
        self.graficador.clear()
        if senal.ndim==1:#grafica un solo canal
            self.graficador.setLabel('left',text='Amplitud(mV)')
            self.graficador.setLabel('bottom',text='cantidad de muestras')
            self.graficador.plot(senal,pen=('r'))
        else:
            DC=10
            for canal in range (senal.shape[0]):#grafica inicialmete todos los canales
                self.graficador.setLabel('left',text='canales desde '+str(0)+' hasta '+str(canal))
                self.graficador.plot(senal[canal,:]+DC*canal)
        self.graficador.repaint();
        
    def graficar_senal_filtrada(self,senalfiltrada,senalorg):#se encarga de graficar la señal filtrada y la señal original para comparar
        self.graficador.clear()
        self.graficador.setLabel('left',text="Señal filtrada(blue) Vs Señal Original(red)")
        self.graficador.plot(senalorg,pen=('r'))
        self.graficador.plot(senalfiltrada[:]+30,pen='b')
        
    def opcion_filtro(self): #recibe la accion del boton filtrar y procede a leer los parametros ingresados por el usuario
        ponderar=str(self.comboPonderar.currentText())
        lambda1=str(self.comboLambda.currentText())
        umbral=str(self.comboUmbral.currentText())
        canal= int(self.Seleccioncanal.text())
        datos1= self.__mi_controlador.devolver_canal(canal, self.__x_min, self.__x_max)
        datos2,correct=self.__mi_controlador.devolver_canal_filtrado(datos1,ponderar,lambda1,umbral)#envia los datos del canal seleccionado al modelo para realizar en este el filtrado 
        print(correct)
        print("dimension señal filtrada: " + str(datos2.shape[0]));
        self.Boton_guarda.setEnabled(True)
        self.__guardar=datos2#guardo en mi variable de vista_grafica los datos obtenidos del filtrado al canal seleccionado 
        self.graficar_senal_filtrada(datos2,datos1)
        
        
    def asignarControlador(self,c):
        self.__mi_controlador = c
        
    def opcion_guardar(self):#recibo la accion del boton guardar y guarda con el nombre de señalfiltrada la informacion de la señal filtrada
        sio.savemat('señalfiltrada',{'Data':self.__guardar})
        print('se guardo exitosamente la señal como archivo (señalfiltrada)')