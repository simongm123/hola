# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 10:56:37 2020
hola 
@author: ESTEBAN MAURICIO
"""
import numpy as np

class Biosenal(object):
    #constructor
    def __init__(self):
        self.__data=np.asarray([])#creo variables en las cuales recibire datos posteriormente desde vista grafica
        self.__canales=0
        self.__puntos=0
        
    def asignarDatos(self,data):#asigno los datos recibidos a las variables del objeto biosenal
        self.__data=data
        self.__canales=data.shape[0]
        self.__puntos=data.shape[1]
    
    #necesitamos hacer operacioes basicas sobre las senal, ampliarla, disminuirla, trasladarla temporalmente etc
    def devolver_segmento(self,x_min,x_max):
        #prevengo errores logicos
        if x_min >= x_max:
            return None
        #cojo los valores que necesito en la biosenal
        return self.__data[:,x_min:x_max]
    
    def devolver_canal(self,canal, x_min, x_max):
        #prevengo errores logicos
        if (x_min >= x_max) and (canal > self.__canales):
            return None
        #cojo los valores que necesito en la biosenal
        return self.__data[canal,x_min:x_max]
    
    
    def devolver_canal_filtrado(self,senal,ponderar,lambda1,umbral):#en esta funcion recibo la señal a filtrar y los parametros parametros registrados por el usuario
        
        signal = np.squeeze(senal);
        longitud_original = signal.shape[0];#guardo el limite de muestras para la señal filtrada
        #descompone la señal a filtrar en aproximaciones y detalles
        def descomponer(signal): #retorna una aproximcion y los detalles
            wavelet = [-1/np.sqrt(2) , 1/np.sqrt(2)];
            scale = [1/np.sqrt(2) , 1/np.sqrt(2)];
            longitud_original = signal.shape[0];
            print(longitud_original);
            senal_descomponer = signal;
        
            if (senal_descomponer.shape[0] % 2) != 0:
                senal_descomponer = np.append(senal_descomponer, 0);
            
            Aprox = np.convolve(senal_descomponer,scale,'full');
            Aprox = Aprox[1::2];
            
            Detail = np.convolve(senal_descomponer,wavelet,'full');
            Detail = Detail[1::2];
            senal_descomponer = Aprox;
            if (senal_descomponer.shape[0] % 2) != 0:
                senal_descomponer = np.append(senal_descomponer, 0);
            
            Aprox2 = np.convolve(senal_descomponer,scale,'full');
            Aprox2 = Aprox2[1::2];
            
            Detail2 = np.convolve(senal_descomponer,wavelet,'full');
            Detail2 = Detail2[1::2];
            senal_descomponer = Aprox2;
            
            if (senal_descomponer.shape[0] % 2) != 0:
                senal_descomponer = np.append(senal_descomponer, 0);
            
            Aprox3 = np.convolve(senal_descomponer,scale,'full');
            Aprox3 = Aprox3[1::2];
            Detail3 = np.convolve(senal_descomponer,wavelet,'full');
            Detail3 = Detail3[1::2];
          
            return [Aprox3,Detail3,Detail2, Detail]
        
        
        def sigmaXlamda(lamda,peso,Detail3,Detail2,Detail): #retorna el lamda multiplicado por el sigma
            stdc = np.zeros((4,1));
            if(peso==1):
              stdc[1] = 1
              stdc[2] = 1
              stdc[3] = 1
            else:
              stdc[1] = (np.median(np.absolute(Detail3)))/0.6745;
              stdc[2] = (np.median(np.absolute(Detail2)))/0.6745;
              stdc[3] = (np.median(np.absolute(Detail)))/0.6745;
                 
            sigmaXlamda1=lamda*stdc[1];
            sigmaXlamda2=lamda*stdc[2];
            sigmaXlamda3=lamda*stdc[3];
            
            return [sigmaXlamda1,sigmaXlamda2,sigmaXlamda3]
        
        def UmbralDuro(detalle,lamda): #retorna un detalle modificado (filtrado)
            det=[]
            for i in detalle:
                if(i<lamda):
                    det.append(0);
                else:
                    det.append(i);
            return det
        
        
        def UmbralSuave(detalle,lamda): #retorna un detalle modificado (filtrado)
            detalle1=[];
            for i in detalle:
                if(i<lamda):
                    detalle1.append(0);
                else:
                    detalle1.append(np.sign(i)*(i-lamda));
            return detalle1        
        
        def Reconstruir (Aprox3,Detail3,Detail2,Detail): #reconstruye la señal ya filtrada
            
            wavelet_inv = [1/np.sqrt(2) , -1/np.sqrt(2)];
            scale_inv = [1/np.sqrt(2) , 1/np.sqrt(2)];
            npoints_aprox = Aprox3.shape[0];
            Aprox_inv3 = np.zeros((2*npoints_aprox));
            Aprox_inv3[0::2] = Aprox3;
            Aprox_inv3[1::2] = 0;    
            APROX3 = np.convolve(Aprox_inv3,scale_inv,'full');    
            npoints_aprox = Detail3.shape[0];
            Detail_inv3 = np.zeros((2*npoints_aprox));
            Detail_inv3[0::2] = Detail3;
            Detail_inv3[1::2] = 0;    
            DETAIL3 = np.convolve(Detail_inv3,wavelet_inv,'full');    
            X3 = APROX3 + DETAIL3;
            if X3.shape[0] > Detail2.shape[0]:
                X3 = X3[0:Detail2.shape[0]];
            npoints_aprox = X3.shape[0];
            Aprox_inv2 = np.zeros((2*npoints_aprox));
            Aprox_inv2[0::2] = X3;
            Aprox_inv2[1::2] = 0;
            APROX2 = np.convolve(Aprox_inv2,scale_inv,'full');   
            npoints_aprox = Detail2.shape[0];
            Detail_inv2 = np.zeros((2*npoints_aprox));
            Detail_inv2[0::2] = Detail2;
            Detail_inv2[1::2] = 0;
            DETAIL2 = np.convolve(Detail_inv2,wavelet_inv,'full');    
            X2 = APROX2 + DETAIL2;    
            if X2.shape[0] > Detail.shape[0]:
                X2 = X2[0:Detail.shape[0]];    
            npoints_aprox = X2.shape[0];
            Aprox_inv = np.zeros((2*npoints_aprox));
            Aprox_inv[0::2] = X2;
            Aprox_inv[1::2] = 0;
            APROX = np.convolve(Aprox_inv,scale_inv,'full');  
            npoints_aprox = Detail.shape[0];
            Detail_inv = np.zeros((2*npoints_aprox));
            Detail_inv[0::2] = Detail;
            Detail_inv[1::2] = 0;
            DETAIL = np.convolve(Detail_inv,wavelet_inv,'full');    
            SIGNAL = APROX + DETAIL;
            SIGNAL = SIGNAL[0:longitud_original];
            
            return SIGNAL

        
        [A3,D3,D2,D]=descomponer(signal);#aplico a la señal signal la funcion descomponer

        Num_samples = A3.shape[0] +  D3.shape[0] + D2.shape[0] + D.shape[0]#guardo el numero de muestras con el que encontrare el lambda
        #comparo los parametros elegidos por el usuario y los guardo en una variable especifica
        if lambda1=="Universal":
            lambdaselec=np.sqrt(2*np.log(Num_samples));
        if lambda1=="MINIMAX":
            lambdaselec= 0.3936 + 0.1829*(np.log(Num_samples)/np.log(2))
        if ponderar=="One":
            ponderarselec=1
        if ponderar=="Single Level Noise":
            ponderarselec=2
        #finalmente comparo que umbral eligio el usuario y aplico el filtro con los parametros anteriores ya seleccionados    
        if umbral=="Suave":
            [LX,LX1,LX2]=sigmaXlamda(lambdaselec,ponderarselec,D3,D2,D)
            #aplico umbral suave a las aproximaciones y detalles
            Det3=UmbralSuave(D3,LX)
            Det2=UmbralSuave(D2,LX1)
            Det=UmbralSuave(D,LX2)
            Det3=np.asarray(Det3)
            Det2=np.asarray(Det2)
            Det=np.asarray(Det)
            
            s=Reconstruir (A3,Det3,Det2,Det);    #ya aplicado el filtro reconstruyo la señal y guardo en la variable s
            
        if umbral=="Duro":
            [LX,LX1,LX2]=sigmaXlamda(lambdaselec,ponderarselec,D3,D2,D)
             #aplico umbral duro a las aproximaciones y detalles
            Det3=UmbralDuro(D3,LX)
            Det2=UmbralDuro(D2,LX1)
            Det=UmbralDuro(D,LX2)  
            Det3=np.asarray(Det3)
            Det2=np.asarray(Det2)
            Det=np.asarray(Det)
            
            s=Reconstruir (A3,Det3,Det2,Det);#ya aplicado el filtro reconstruyo la señal y guardo en la variable s   
        a="Filtrado Exitoso"
        return(s,a)#retorno a vista grafica la señal ya filtrada lista a graficar y un mensaje de confirmacion