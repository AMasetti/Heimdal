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


#PuertoUDP="$(sudo lsof -i :5000|grep -oP '(?<=python  ).*?(?= augusto)')"
#sudo kill -9 $puertoUDP


#sudo kill -9 $(sudo lsof -i :5000|grep -oP '(?<=python  ).*?(?= augusto)')

#sudo lsof -i :5000|grep -oP '(?<=python  ).*?(?= root)'
#puertoUDP=sudo lsof -i :5000|grep -oP '(?<=python  ).*?(?= root)'

#sudo kill -9 8704|sudo lsof -i :5000|grep -oP '(?<=python  ).*?(?= root)'

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

print('Sistemas listos, iniciando en 2 segundos')

time.sleep(2)

Right,Left,Rows = JC.UPPRecieve(Socket,verbose=0)

Right,Left = JC.DataFormatForCorrelationUDP(Left,Right,SampleRate)

Correlacion,ArgMaxT = JC.FastFourierCorrelationFiltered(Right,Left)

try:

	DeltaT,Angulo = JC.ITDAngleFind(ArgMaxT,Rows,SampleRate,Rows/SampleRate)

	Angulo = JC.AngleParser(AnguloPrevio+Angulo)

	JC.AngleSetPoint(Angulo,Serial)

except:

	DeltaT,Angulo = JC.ITDAngleFind(ArgMaxT,Rows,SampleRate,Rows/SampleRate)

	Angulo = JC.AngleParser(AnguloPrevio+Angulo)

	JC.AngleSetPoint(Angulo,Serial)

AnguloPrevio = Angulo

while True:

	
	Right,Left,Rows = JC.UPPRecieve(Socket,verbose=0)

	Right,Left = JC.DataFormatForCorrelationUDP(Left,Right,SampleRate)

	Correlacion,ArgMaxT = JC.FastFourierCorrelationFiltered(Right,Left)

	try: 

		DeltaT,Angulo = JC.ITDAngleFind(ArgMaxT,Rows,SampleRate,Rows/SampleRate)
		
		Angulo = JC.AngleParser(AnguloPrevio+Angulo)

		AnguloPrevio = JC.AngleSetPoint_Verify(Angulo,Serial,AnguloPrevio)

	except:

	 	print 'Error on sample'

Serial.close()
Socket.close