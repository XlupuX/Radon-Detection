# coding: utf-8
import serial
import time
import sys
import alarm
import datetime as dt
import os


def Connection():
	try:
		ser = serial.Serial('/dev/ttyACM0', 115200)
		print("Port found and connected")  # Connessione alla porta seriale
		return ser
	except:
		print("Error. Check port")
		return -1


def Send(ser, cmd):
	print("Got command: " + str(cmd) + "  Now writing")
	line = ser.write(cmd)  # Scrittura comando
	print(str(cmd) + " Sent to serial")

	print("\n")

	print("Waiting reply")
	response = int(ser.readline())  # Attesa conferma
	print("Got reply: " + str(response))
	if response == 121:
		return 0
	elif response == 1:
		return 1
	else:
		return -1


def Listening(ser):
	bip = int(ser.readline())
	return bip


def getStringTime():
	ts = time.time()
	st = dt.datetime.fromtimestamp(ts).strftime('%d\%m\%Y-%H:%M:%S')
	return st


def saveFile(fileToSave, N_file):
	# Salva il file passato
	fileToSave.close()
	# Prende l'ora corrente
	fileName = 'File' + str(N_file) + '.txt'
	# Genera il nuovo file con la data come nome
	newFile = open(str(fileName), "w")
	currentTimeString = getStringTime()
	newFile.write("Detection starts at: " + currentTimeString + "\n")

	return newFile


def calculateDelta(startTimeInS, finishTimeInS):
	deltaInSeconds = finishTimeInS - startTimeInS

	return deltaInSeconds


def Numero_ricevuto(numero):
	if numero == 33:
		#If 33 is received, Arduino blocked all comunications (Decidere cosa fare!!!)
		#os.system('reboot')
		print("Arduino blocked all the activities!")
	if numero == 107:
		serial.write('121')


def main():
	# Declaring the variable which counts how many detection we made at the start in order to get detection even during
	# startup checks
	bip_tot = 0

	#Initiate connection with Arduino
	ser = Connection()

	# If there's an error while connecting, connection() returns -1
	if(ser == -1):

		# Connection failed: exiting the script
		sys.exit()

	else:

		# Connection established, turn on the status LED and make a check (code for checking: 107)
		check = Send(ser, str(107))
		time.sleep(1.5)

	if(check == -1):

        # Check failed: Arduino isn't working
		sys.exit("Arduino doesn't reply")
	elif(check == 1):
		bip_tot += 1

    # Code for file saving
	fileNumber = 1

    # Creates the first logging file, named "File1.txt". Following files will be named "File2.txt", "File3.txt"...
	currentLog = open('File' + str(fileNumber) + '.txt',"w")

    # Gets the current time and writes it on the log file
	currentTimeString = getStringTime()
	currentLog.write("Detection starts at: " + currentTimeString + "\n")

    # Gets the detection starting time in seconds
	startTimeInS = time.time()
	startTimeWrite = time.time()

    # At this point Arduino's working and python can start listening for signals (bip)
	while 1:

        # Every fourth of an hour it prints the time along with how many detection it made and checks if Arduino's
        # working
		finishTimeWrite = time.time()
		if calculateDelta(startTimeWrite, finishTimeWrite) >= 900:
			currentLog.write(getStringTime() + ',' + str(bip_tot))  # fa il timestamp dell'ultimo  quarto d'ora''
			startTimeWrite = time.time()
			bip_tot = 0
			Check = Send(ser, str(107))
			if Check == -1:
				saveFile(currentLog, fileNumber)
				sys.exit("Arduino doesn't reply")
			elif (check == 1):
				bip_tot += 1

        # Every hour it saves the log and it creates a new one
		finishTimeInS = time.time()
		if calculateDelta(startTimeInS, finishTimeInS) >= 3600:

			fileNumber += 1
			currentLog = saveFile(currentLog, fileNumber)
			startTimeInS = time.time()

        # Following code puts a maximun waiting time for a detection to arrive, if nothing arrives in 300 s, it breaks
        # the listening and checks if Arduino's working

		maxWaitingTime = 300  # Seconds
		bip = 0

		try:
			with alarm.Timeout(id_='a', seconds=maxWaitingTime):
				bip = Listening(ser)

		except alarm.TimeoutError as e:  # No impulses for 5 minutes
			print('raised', e.id_)

			Check = Send(ser, "107")  # controlla se arduino funge
			if Check == -1:
				saveFile(currentLog, fileNumber)
				sys.exit("Arduino doesn't reply")

        # If a detection happened, increase the detection count variable
		if bip == 1:
			bip_tot += 1
		else:
			Numero_ricevuto(bip)


if __name__ == "__main__":
	sys.exit(main())
