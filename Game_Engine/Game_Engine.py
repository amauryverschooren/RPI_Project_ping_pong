#!/usr/bin/python3
import paho.mqtt.client as mqtt
import urllib.request
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#GLOBALS
hello_topic = "setup/hello"
ball_topic, racket_topic, control_topic = "game/ball", "game/racket", "game/controller"
controller_flag = 0
ball_flag = 0
canvas_width = 600
canvas_height = 400
ball_dimensions = [20,20]
racket_dimensions = [10,100]


client = mqtt.Client(client_id="Game_engine", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")



class Ball:
	def __init__(self, xPos, yPos):
		self.positionX = xPos
		self.positionY = yPos
		self.x_heading = 1
		self.y_heading = 1
	def send_position(self):
		client.publish(ball_topic, str(self.positionX) + "; " + str(self.positionY))
	def update_position(self):
		self.positionX = self.positionX + (2 * self.x_heading)
		self.positionY = self.positionY + (2 * self.y_heading)
		if self.positionX >= canvas_width -20:
			self.x_heading = -1
		if self.positionY >= canvas_height -20:
			self.y_heading = -1
		if self.positionX <= 0:
			self.x_heading = 1
		if self.positionY <= 0:
			self.y_heading = 1
		print(self.positionX)
		print(self.positionY)
		self.send_position()
class Racket:
	def __init__(self, xPos,yPos,number):
		self.playerNumber = number
		self.xPosition = xPos
		self.yPosition = yPos
	def update_position(self, input_number):
		self.yPosition += input_number
		print("position racket: " + str(self.playerNumber) + " updated!")
		self.send_position()
	def send_position(self):
		client.publish(racket_topic, "RACKET_"+str(self.playerNumber)+"; POSITION=" + str(self.yPosition))
		
		

#aanmaken bal en pads
Ball = Ball(((canvas_width/2)-(ball_dimensions[0]/2)), ((canvas_height/2)-(ball_dimensions[1]/2)))
Racket1 = Racket(canvas_width - canvas_width +1, canvas_height/2-racket_dimensions[1]/2,1)
Racket2 = Racket(canvas_width - 1, canvas_height/2-racket_dimensions[1]/2,2)



	
def on_connect(client, userdata, flags, rc):
	if rc==0:
		print("connected OK Returned code=",rc)
	else:
		print("Bad connection Returned code=",rc)
def on_message(client, userdata, msg):

	global controller_flag
	global ball_flag
	print(msg.topic+" message payload is {}".format(msg.payload.decode("utf-8")))
	msg.payload = msg.payload.decode("utf-8")
	if msg.topic == "setup/hello":
		if controller_flag == 0:
			if msg.payload == "ID=Controller_A":
				print("Bericht is van Controller A")
				controller_flag = 1
				message = "ID=Controller_A; PLAYERNUMBER=1"
				publish_hello(message)
			if msg.payload == "ID=Controller_B":
				print("Bericht is van Controller B")
				controller_flag = 1
				message = "ID=Controller_B; PLAYERNUMBER=1"
				publish_hello(message)
		elif controller_flag == 1:
			ball_flag = 1
			if msg.payload == "ID=Controller_A":
				print("Bericht is van Controller A")
				controller_flag = 0
				message = "ID=Controller_A; PLAYERNUMBER=2"
				publish_hello(message)
			if msg.payload == "ID=Controller_B":
				print("Bericht is van Controller B")
				controller_flag = 0
				message = "ID=Controller_B; PLAYERNUMBER=2"
				publish_hello(message)
	elif msg.topic == "game/bal":
		print("azerf")
	elif msg.topic == "game/controller":
		splittedString = msg.payload.split("; ")
		if splittedString[1] == "PAD_UP":
			if splittedString[0] == "PLAYERNUMBER=1":
				Racket1.update_position(15)
			elif splittedString[0] == "PLAYERNUMBER=2":
				Racket2.update_position(15)
		if splittedString[1] == "PAD_DN":
			if splittedString[0] == "PLAYERNUMBER=1":
				Racket1.update_position(-15)
			elif splittedString[0] == "PLAYERNUMBER=2":
				Racket2.update_position(-15)
def publish_hello(message):
	client.publish(hello_topic, message)
	print("Controller hello message send")


client.on_connect = on_connect
client.on_message = on_message
client.connect("213.119.34.109", 1888, 60)
client.subscribe([(hello_topic,0),(racket_topic,0),(control_topic,0)])
ball_topic, racket_topic, control_topic
client.loop_start()
while ball_flag == 0:
	print("qsdfv")
while ball_flag == 1:
	time.sleep(0.1)
	Ball.update_position()