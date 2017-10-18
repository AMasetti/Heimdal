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

global Right,Left,Ampel



#-----Hilo Principal-----

JC.PrintClassic()

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

DataWAV,SampleRate,Rows,Columns=JC.WAV_2_Numpy('i45.wav')

Right,Left = JC.DataFormatForCorrelation(DataWAV,SampleRate)

Correlacion,ArgMaxT = JC.FastFourierCorrelationFiltered(Right,Left)

try:

	DeltaT,Angulo = JC.ITDAngleFind(ArgMaxT,Rows,SampleRate,Rows/SampleRate)

	Angulo = JC.AngleParser(Angulo)

	JC.AngleSetPoint(Angulo,Serial)

except:

	print 'Error de Calculo :(' 

AnguloPrevio = Angulo

print Angulo


time.sleep(2)

DataWAV,SampleRate,Rows,Columns = JC.WAV_2_Numpy('paneo.wav')
print ''
print 'Muestras del Paneo: ',Rows
BufferTime=1
Iteracion=0

for x in range(0,Rows,int(SampleRate*BufferTime)):

	Right,Left = JC.DataFormatForCorrelation(DataWAV[x:x+int(SampleRate*BufferTime),:],int(SampleRate*BufferTime))

 	Correlacion,ArgMaxT = JC.FastFourierCorrelationFiltered(Right,Left)

	try:

		DeltaT,Angulo = JC.ITDAngleFind(ArgMaxT,Rows,SampleRate,BufferTime)

		Angulo = JC.AngleParser(Angulo)

		JC.AngleSetPoint(Angulo,Serial)

		time.sleep(0.1)

	except:

		print 'Error de Calculo :(' 

	AnguloPrevio = Angulo

	print Angulo


Serial.close()


