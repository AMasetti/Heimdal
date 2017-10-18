#  ______ _____ ______ _____                     _    _ _   _ _____  
# |  ____/ ____|  ____|_   _|   /\              | |  | | \ | |  __ \ 
# | |__ | |    | |__    | |    /  \     ______  | |  | |  \| | |__) |
# |  __|| |    |  __|   | |   / /\ \   |______| | |  | | . ` |  _  / 
# | |   | |____| |____ _| |_ / ____ \           | |__| | |\  | | \ \ 
# |_|    \_____|______|_____/_/    \_\           \____/|_| \_|_|  \_\
                                                                    
                                                                                                                                                                                                                                              
# Facultad de Ciencias Exactas Ingenieria y Agrimensura - Universidad Nacional de Rosario            
#
# MASETTI, Augusto
#
# Octubre de 2017  

import scipy.io.wavfile
import numpy as np
import numpy.fft as npfft
import math
import serial
import os
import socket
import time
from time import sleep   
from matplotlib import pyplot as plt                                                                                                                                                                           


def AngleSetPoint_Verify(Angle,Serial,Prev):
	
	# Muevo el servo conectado al Arduino en un valor determinado siempre que el mismo no supere un valor de
	# threshold. Se ignoran entonces variaciones bruscas en el movimiento garantizando un movimiento continuo
	# Toma como entrada los dos angulos, el de set-point y el angulo anterior, asi como tambien el objeto de 
	# la conexion serial. Retorna el nuevo valor previo del angulo.

	if abs(Prev-Angle)<20:
		Serial.write(chr(Angle))
		Prev = Angle
		Resp=Serial.readline()
		
	return Prev

def AngleSetPoint(Angle,Serial):
	
	# Muevo el servo conectado al Arduino en un valor determinado 
	# Toma como entrada el angulo de set-point y el objeto de 
	# la conexion serial.
	
	Serial.write(chr(Angle))
	
def EstablishConnectionSiOSi():
	
	# Establece una conexion serial entre un sistema corriendo Linux y un Arduino de forma automatica
	# Retorna el objeto de conexion serie establecido o da a conocer por pantalla que no hay dispositivos 
	# en los puertos especifiados

	success=0

	Port=['/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2'] #Completar con los posibles puertos a los cuales se puede conectar el Arduino
	for i in range(0,len(Port)):
		try:
			CMD = 'sudo chmod 666 '
			CMD += Port[i]
			os.system(CMD)
			success=1
			ser = serial.Serial(Port[i], 9600) 
			time.sleep(1)
		except:
			success=0
			print "No hay dispositivos en el puerto: ", Port[i]
		if success==1:
			print "Dispositivo conectado al puerto: ", Port[i]
			break
	return ser
                                                                                                                                                                                    
def WAV_2_Numpy(Directory):
	
	# Obtiene los datos de un archivo en formato '.wav' y los traduce a una matriz de Numpy
	# Como variable de entrada se envia el directorio que aloja el archivo. Retorna la matriz
	# de datos DataWAV, la frecuencia de muestreo, asi como la cantidad de filas y columnas.
	#
	# Ejemplo de uso:
	# DataWAV,SampleRate,rows,columns=WAV_2_Numpy('/Desktop/i30.wav')

	SampleRate,DataWAV = scipy.io.wavfile.read(Directory, mmap=False)
	Rows,Columns=DataWAV.shape
	return DataWAV,SampleRate,Rows,Columns

def DataFormatForCorrelation(DataWAV,SampleRate):
	
	# Prepara la informacion contenda en las matrices que se caluclaron con la funcion WAV_2_Numpy()
	# para poder calcular luego la correlacion cruzada
	#
	# Prepare the data of a sound file for ITD computation
	#
	# Ejemplo de uso:
	# Right,Left=DataFormatForCorrelation(DataWAV,SampleRate)

	BlockOfNothingness=np.zeros((SampleRate,1))
	Left=DataWAV[:,0]
	Right=DataWAV[:,1]
	Left=np.append(BlockOfNothingness,Left)
	Right=np.append(Right, BlockOfNothingness)
	Left=Left[:,np.newaxis]
	Right=Right[:, np.newaxis]
	return Right,Left

def FastFourierCorrelation(Array1,Array2):

	# Computa la correlacion cruzada entre dos seniales pasadas como argumento utilizando la propiedad
	# de multiplicacion en el plano frecuencial y la transformada rapida de Fourier. Retorna la matriz de 
	# correlacion cruzada y la posicion del maximo argumento de dicha matriz.
	#
	# Compute the cross correlation of two signals using the propierty of multiplication in the frecuencial plane, and
	# find theposition of the maximum value
	#
	# Ejemplo de uso
	# corr,pos=FastFourierCorrelation(Right,Left)

	Corr=npfft.ifft(np.multiply(npfft.fft(Array1,axis=0), npfft.fft(np.flipud(Array2),axis=0)),axis=0)
	Pos=float(np.argmax(Corr))	
	return Corr,Pos

def FastFourierCorrelationFiltered(Array1,Array2):

	# Computa la correlacion cruzada entre dos seniales pasadas como argumento utilizando la propiedad
	# de multiplicacion en el plano frecuencial y la transformada rapida de Fourier. Retorna la matriz de 
	# correlacion cruzada y la posicion del maximo argumento de dicha matriz.
	#
	# Compute the cross correlation of two signals using the propierty of multiplication in the frecuencial plane, and
	# find theposition of the maximum value
	#
	# Ejemplo de uso
	# corr,pos=FastFourierCorrelation(Right,Left)

	First=npfft.fft(Array1,axis=0)
	Second=npfft.fft(np.flipud(Array2),axis=0)
	Corr=np.real(npfft.ifft(np.multiply(First,Second),axis=0))
	Pos=(np.argmax(Corr))	
	Corr[Pos]=0
	Pos=(np.argmax(Corr))	
	Pos=float(np.argmax(Corr))	
	return Corr,Pos

def DataFormatForCorrelationUDP(Left,Right,SampleRate):

	# Prepara los datos para el calculo de la correlacion cruzada de datos recibidos por UDP
	# Prepare the data of a sound file for ITD computation
	#
	# Ejemplo de uso:
	# Right,Left=DataFormatForCorrelation(DataWAV,SampleRate)

	BlockOfNothingness=np.zeros((SampleRate,1))
	Left=np.append(BlockOfNothingness,Left)
	Right=np.append(Right, BlockOfNothingness)
	Left=Left[:,np.newaxis]
	Right=Right[:, np.newaxis]
	return Right,Left

def ITDAngleFind(Pos,Rows,SampleRate,BufferTime,IEDistance=0.2,SoundSpeed=340.29):
	
	# Computo el angulo del cual proviene el sonido y la diferencia de teimpo de arrivo entre los dos microfonos
	# Compute the ITD between 2 signals and the angle from which the source originated them
	#
	# Ejemplo de uso:
	# TimeDelay,Angle=ITDAngleFind(pos,rows,SampleRate)

	TimeDelay=(Pos-(SampleRate*BufferTime))/SampleRate
	Angle=math.degrees(math.asin(SoundSpeed*TimeDelay/IEDistance))
	return TimeDelay,Angle

def AudioDataVerbose(SampleRate,rows,corr,pos,TimeDelay,Angle):
	
	# Obtengo una respuesta por pantalla de los datos tratados
	# Get feedback from the process through the console
	#
	# Ejemplo de uso:
	# AudioDataVerbose(SampleRate,rows,corr,pos,TimeDelay,Angle)
	
	print 'Muestras por Segundo: ', SampleRate
	print 'Cantidad de datos: ',rows
	print 'Forma de la Correlacion cruzada: ',corr.shape
	print 'Posicion del maximo argumento: ',pos
	print 'ITD: ',TimeDelay
	print 'Angulo: ',Angle				

def PlotCorrelation(Corr):
	
	#Ploteo continuo de graficos de correlacion	

	plt.ion()
	plt.cla()
	plt.plot(np.real(Corr))
	plt.draw()
	plt.pause(0.001)

def ConnectUDP(IP='192.168.0.108',port=5000):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((IP, port))
	print "Esperando en el puerto: ", port
	return s

def UDPSendInstance(IP='192.168.0.108',port=5000,MSG='Wubba Lubba Dubdub !'):

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(MSG, (IP, port))
	sock.close

def UPPRecieve(s,verbose=0):


	data, addr = s.recvfrom(1024)
	paquetnum=  int(''.join(str(ord(c)) for c in data[1:2]))
	datasntchnl= int(''.join(str(ord(c)) for c in data[3:4]))
	l=0
	r=0
	Left=numpy.zeros(datasntchnl)
	Right=numpy.zeros(datasntchnl)
	for i in range(5,datasntchnl*2+5,2):
		Left[l] =  int(''.join(str(ord(c)) for c in data[i:i+1]))
	 	l=l+1
	for i in range(datasntchnl*2+6,datasntchnl*4+6,2):
		Right[r] =  int(''.join(str(ord(c)) for c in data[i:i+1]))
		r=r+1
	if verbose==1:
		print 'Numero de paquete: ', paquetnum
		print 'Cantidad de datos por canal: ', datasntchnl

	Data=[Left[:],Right[:]]
	return Right,Left,r

def KillUDPProcesses():

	CMD="sudo kill -9 $(sudo lsof -i :5000|grep -oP '(?<=python  ).*?(?= augusto)')" #Reemplazar augusto por el usuario que aparece haciendo lsof -i :5000
	os.system(CMD)
	CMD="sudo kill -9 $(sudo lsof -i :5000|grep -oP '(?<=python  ).*?(?= root)')"
	os.system(CMD)

def AngleParser(Angle):
	if Angle>0:
			direccion='Izquierda'
			Angle=90-Angle
			Angle = int(Angle)
			
			# ArduinoComm.AngleSetPoint(Angle,ser)

	else:
		direccion="Derecha"
		Angle=abs(Angle)
		Angle=90+Angle
		Angle = int(Angle)
	return Angle
			
def PrintClassic():
	Logo=['  ______ _____ ______ _____                     _    _ _   _ _____ ',' |  ____/ ____|  ____|_   _|   /\              | |  | | \ | |  __ \ ',' | |__ | |    | |__    | |    /  \     ______  | |  | |  \| | |__) |',' |  __|| |    |  __|   | |   / /\ \   |______| | |  | | . ` |  _  / ',' | |   | |____| |____ _| |_ / ____ \           | |__| | |\  | | \ \ ','# |_|    \_____|______|_____/_/    \_\           \____/|_| \_|_|  \_\]']
	
	for j in range (0,5):
		print Logo[j]
	
