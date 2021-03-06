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

import JONICASLib as JC
import time
import serial
import socket
import numpy
import threading
from time import sleep


def ReadDaemon():

	global StackLeftDef,StackRightDef

	while StopT1==0:

		StackRight = list()
		StackLeft = list()

		for i in range(0,25,1):

			Right=np.zeros([1764,1])
			Left=np.zeros([1764,1])
			Rows=1764

			# Right,Left,Row = JC.UPPRecieve(Socket,verbose=0)

			# print Right.shape

			Right,Left = JC.DataFormatForCorrelationUDP(Right,Left,SampleRate)

			StackRight.append(Right)
			StackLeft.append(Left)

		StackLeftDef=StackLeft
		StackRightDef=StackRight

		#print len(StackRight)


def FFTandAngle():

	global CorrelacionDef,ArgMaxTDef

	while StopT2==0:

		Corr= list()
		ArgMax = list()

		for i in range(0,len(StackRightDef),1):
			
			try:
				Correlacion,ArgMaxT = JC.FastFourierCorrelationFiltered(StackRightDef[i],StackLeftDef[i])
				Corr.append(Correlacion)
				ArgMax.append(ArgMaxT)
			except:
			
				print 'Error: No data'

		ArgMaxTDef=ArgMax
		CorrelacionDef=Corr
		# print len(Corr)

#-----Variables Globales-----

global Rigth,Left,Ampel

SampleRate=44100
BufferTime=1
Iteracion=0


#-----Hilo Principal-----

JC.PrintClassic()

print('Iniciando Socket UDP...')

JC.KillUDPProcesses()

Socket = JC.ConnectUDP('192.168.0.108',5000)

print('Socket Listo !')

print('Iniciando conexion por UART...')

try:
	Serial = JC.EstablishConnectionSiOSi()

except:

	print 'No hay dispositivos Arduino conectados'

time.sleep(1)

print('Probando Servos...')

JC.AngleSetPoint(0,Serial)

time.sleep(1)

JC.AngleSetPoint(180,Serial)

time.sleep(1)

JC.AngleSetPoint(90,Serial)

AnguloPrevio=90

print('Iniciando Procesamiento Multi-Hilo')

StopT1 = 0
StopT2 = 0

T1 = threading.Thread(target=ReadDaemon)
T1.setDaemon(True)
T1.start()

time.sleep(0.25)

T2 = threading.Thread(target=FFTandAngle)
T2.setDaemon(True)
T2.start()

time.sleep(1)

print('Sistemas listos, iniciando en 2 segundos')

time.sleep(2)

while True:

	for i in range(0,len(StackRightDef),1):
		# try:

		DeltaT,Angulo = JC.ITDAngleFind(ArgMaxTDef[i],1764,SampleRate,1764/SampleRate)

		Angulo = JC.AngleParser(AnguloPrevio+Angulo)

		AnguloPrevio = JC.AngleSetPoint_Verify(Angulo,Serial,AnguloPrevio)

		print i,' El angulo es: ', Angulo

		# except:

			# print 'Error de caluclo :('
		time.sleep(0.01)


Serial.close()
Socket.close