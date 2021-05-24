#!/usr/bin/python3
import paho.mqtt.client as mqtt
import urllib.request
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#GLOBALS
hello_topic = "setup/hello"
ball_topic = "game/bal"
racket_topic = "game/racket"
controller_flag = 0
canvas_width = 600
canvas_height = 400
ball_dimensions = [20,20]
racket_dimensions = [15,80]



class Ball:
	def __init__(xPos, yPos)
		positionX = xPos
		positionY = yPos
	def send_position
		client.publish(ball_topic, "POSITION_X=" + str(positionX))
		client.publish(ball_topic, "POSITION_Y=" + str(positionY))
class Racket:
	def __init__(xPos,yPos,number)
		positionX = xPos
		positionY = yPos
		player = number
	def send_position
		client.publish(racket_topic, "RACKET_"+player+"_POSITION_Y=" + str(positionY))

#aanmaken bal en pads
Ball = Ball(canvas_width/2-ball_dimensions[0]/2, canvas_height/2-ball_dimensions[1]/2)
Racket1 = Racket(canvas_width - canvas_width +1, canvas_height/2-racket_dimensions[1]/2,1)
Racket2 = Racket(canvas_width - 1, canvas_height/2-racket_dimensions[1]/2,2)



	
def on_connect(client, userdata, flags, rc):
	if rc==0:
		print("connected OK Returned code=",rc)
	else:
		print("Bad connection Returned code=",rc)

def on_message(client, userdata, msg):

	global controller_flag

	print(msg.topic+" message payload is {}".format(msg.payload.decode("utf-8")))
	msg.payload = msg.payload.decode("utf-8")
	if msg.topic == "setup/hello"
		if controller_flag == 0:
			if msg.payload == "ID=Controller_A":
				print("Bericht is van Controller A")
				controller_flag = 1
				message = "ID=Controller_A; CONTROLLERNUMBER=1"
				publish_hello(message)
			if msg.payload == "ID=Controller_B":
				print("Bericht is van Controller B")
				controller_flag = 1
				message = "ID=Controller_B; CONTROLLERNUMBER=1"
				publish_hello(message)
		elif controller_flag == 1:
			if msg.payload == "ID=Controller_A":
				print("Bericht is van Controller A")
				controller_flag = 0
				message = "ID=Controller_A; CONTROLLERNUMBER=2"
				publish_hello(message)
			if msg.payload == "ID=Controller_B":
				print("Bericht is van Controller B")
				controller_flag = 0
				message = "ID=Controller_B; CONTROLLERNUMBER=2"
				publish_hello(message)
	elif msg.topic == "game/bal"
	elif msg.topic == "game/racket"
			
def publish_hello(message):
	client.publish(hello_topic, message)
	print("Controller hello message send")

client = mqtt.Client(client_id="Game_engine", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
client.on_connect = on_connect
client.on_message = on_message
client.connect("213.119.34.109", 1888, 60)
client.subscribe(hello_topic)
client.loop_forever()
