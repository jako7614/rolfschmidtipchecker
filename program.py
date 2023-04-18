# import RPi.GPIO as GPIO
from pythonping import ping
import time
from datetime import datetime
import mysql.connector
 
 

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21
 
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
 
# GPIO.setup(Relay_Ch1,GPIO.OUT)
# GPIO.setup(Relay_Ch2,GPIO.OUT)
# GPIO.setup(Relay_Ch3,GPIO.OUT)
 
print("Setup The Relay Module is [success]")

# GPIO.output(Relay_Ch1,GPIO.HIGH)
# print("Channel 1:The Common Contact is access to the Normal Closed Contact!")

# GPIO.output(Relay_Ch2,GPIO.HIGH)
# print("Channel 2:The Common Contact is access to the Normal Closed Contact!")

# GPIO.output(Relay_Ch3,GPIO.HIGH)
# print("Channel 3:The Common Contact is access to the Normal Closed Contact!")
 
counter = 0
lastState = "Off"
offset = 10

mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		password="Had03834",
		database="rolfschmidttest"
	)

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM machineip")
ips = mycursor.fetchall()

def writeToDatabaseRelay(state):
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		password="Had03834",
		database="rolfschmidttest"
	)

	mycursor = mydb.cursor()
	
	if state == "On":
		sql = "INSERT INTO relaylog (state) VALUES (1)"
	elif state == "Off":
		sql = "INSERT INTO relaylog (state) VALUES (0)"
	mycursor.execute(sql)
	mydb.commit()

def writeToDatabaseIp(ip, state):
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		password="Had03834",
		database="rolfschmidttest"
	)

	mycursor = mydb.cursor()
	sql = "INSERT INTO iplog (address, state) VALUES (%s, %s)"

	if state == "On":
		val = (ip, 1)
	elif state == "Off":
		val = (ip, 0)
	mycursor.execute(sql, val)
	mydb.commit()


def pingTest(hostname):
	global counter
	output = ping(hostname["ip"])
	for reply in output:
		if reply  and ("Reply from" and "bytes in") in str(reply):
			print(hostname["ip"], " is on")
			if hostname["lastState"] == "Off":
				writeToFileIp(hostname["ip"], "On")
			hostname["lastState"] = "On"
			counter = 0
			# return(True)
		else:
			print(hostname["ip"], " is off")
			if hostname["lastState"] == "On":
				writeToFileIp(hostname["ip"], "Off")
			hostname["lastState"] = "Off"
			counter += 1

def pingTest2():
	global counter
	global ips
	mydb = mysql.connector.connect(
		host="localhost",
		user="root",
		password="Had03834",
		database="rolfschmidttest"
	)

	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM machineip")
	ips = mycursor.fetchall()

	for x in ips:
		output = ping(x[2])
		for reply in output:
			if reply  and ("Reply from" and "bytes in") in str(reply):
				print(x[2], " is on")
				if x[3] == 0:
					writeToDatabaseIp(x[2], "On")
					sql = "UPDATE machineip SET lastState = '1' WHERE ip = '{0}'".format(x[2])
					mycursor.execute(sql)
					mydb.commit()
				counter = 0
				break
			else:
				print(x[2], " is off")
				if x[3] == 1:
					writeToDatabaseIp(x[2], "Off")
					sql = "UPDATE machineip SET lastState = '0' WHERE ip = '{0}'".format(x[2])
					mycursor.execute(sql)
					mydb.commit()
				counter += 1
				break
 
try:
 
	try:
		import httplib
	except:
		import http.client as httplib
 
	def haveInternet():
		conn = httplib.HTTPConnection("www.google.com", timeout=5)
		try:
			conn.request("HEAD", "/")
			conn.close()
			return True
		except:
			conn.close()
			return False
 
	connection = haveInternet()
 
 
	while True:
 
		if connection == True:
 
			if (counter % len(ips)) != 0:
				counter = 0
			print(counter)
			if counter >= len(ips) * 3:
				if lastState == "Off":
					# GPIO.output(Relay_Ch1,GPIO.LOW)
					print("Channel 1:The Common Contact is access to the Normal Open Contact!")
					writeToDatabaseRelay("On")
					lastState = "On"
			else:
				if lastState == "On":
					# GPIO.output(Relay_Ch1,GPIO.HIGH)
					print("Channel 1:The Common Contact is access to the Normal Closed Contact!")
					writeToDatabaseRelay("Off")
					lastState = "Off"
 
			pingTest2()
 
			time.sleep(offset)
			connection = haveInternet()
		elif connection == False:
			print("No internet connection")
			# GPIO.output(Relay_Ch1,GPIO.HIGH)
			# print("Channel 1:The Common Contact is access to the Normal Closed Contact!")
 
			# GPIO.output(Relay_Ch2,GPIO.HIGH)
			# print("Channel 2:The Common Contact is access to the Normal Closed Contact!")
 
			# GPIO.output(Relay_Ch3,GPIO.HIGH)
			# print("Channel 3:The Common Contact is access to the Normal Closed Contact!")
			time.sleep(offset)
		# 	connection = haveInternet()
 
except:
	print("except")
	# GPIO.cleanup()