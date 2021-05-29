#!/usr/bin/python3
import paho.mqtt.client as mqtt
import urllib.request
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#GLOBALS
state_topic, hello_topic, ball_topic, racket_topic, control_topic, led_topic, score_topic = "game/state", "setup/hello", "game/ball", "game/racket", "game/controller", "game/led", "game/score"
controller_flag = 0
ball_flag = 0
canvas_width = 600
canvas_height = 400
ball_dimensions = [20,20]
racket_dimensions = [10,100]
rounds = 1
end_game_flag = False


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
		print(str(self.positionX) + " - " + str(self.positionY))
		self.check_collision_pad()
	def check_collision_pad(self):
		if self.positionX + 20 >= canvas_width:
			self.new_round()
		elif self.positionX <= 0:
			self.new_round()
		elif self.positionX + 20 >= (canvas_width - (20 + racket_dimensions[0])):
			if (self.positionY + 20) < (Racket2.yPosition + racket_dimensions[1]) and self.positionY > Racket2.yPosition:
				if (self.positionX +20) <= (canvas_width - 20):
					print("trigger collision pad")
					self.x_heading = -1
					Racket2.score += 5
					print("dit is de score van speler 2: " + str(Racket2.score))
					client.publish(score_topic, "PLAYER_"+str(Racket2.playerNumber)+"; SCORE=" + str(Racket2.score))
		elif self.positionX <= (20 + racket_dimensions[0]):
			if (self.positionY + 20) < (Racket1.yPosition + racket_dimensions[1]) and self.positionY > Racket1.yPosition:
				if self.positionX >= 20:
					print("trigger collision pad")
					self.x_heading = 1
					Racket1.score += 5
					print("dit is de score van speler 1: " + str(Racket1.score))
					client.publish(score_topic, "PLAYER_"+str(Racket1.playerNumber)+"; SCORE=" + str(Racket1.score))
		self.send_position()
	def new_round(self):
		print("nieuwe ronde")
		global rounds
		global end_game_flag
		rounds += 1 if rounds < 10 else 0
		print(rounds)
		if rounds == 10:
			end_game_flag = True
		self.positionX = ((canvas_width/2)-(ball_dimensions[0]/2))
		self.positionY = ((canvas_height/2)-(ball_dimensions[1]/2))

class Racket:
	def __init__(self, xPos,yPos,number):
		self.playerNumber = number
		self.xPosition = xPos
		self.yPosition = yPos
		self.score = 0
		self.racketVelocity = 1
		self.high_speed_triggered = False
	def update_position(self, input_number):
		if self.yPosition + input_number < 0 or self.yPosition + racket_dimensions[1] + input_number > canvas_height:
			self.yPosition = self.yPosition
		else:
			self.yPosition += (input_number * self.racketVelocity)
			print("position racket: " + str(self.playerNumber) + " updated!")
			self.send_position()
	def update_velocity(self):
		if self.high_speed_triggered == False:
			self.racketVelocity = 2
		else:
			self.racketVelocity = 1
	def send_position(self):
		client.publish(racket_topic, "RACKET_"+str(self.playerNumber)+"; POSITION=" + str(self.yPosition))
		
		

#aanmaken bal en pads
Racket1 = Racket(canvas_width - canvas_width +1, canvas_height/2-racket_dimensions[1]/2,1)
Racket2 = Racket(canvas_width - 1, canvas_height/2-racket_dimensions[1]/2,2)
Ball = Ball(((canvas_width/2)-(ball_dimensions[0]/2)), ((canvas_height/2)-(ball_dimensions[1]/2)))




	
def on_connect(client, userdata, flags, rc):
	if rc==0:
		print("connected OK Returned code=",rc)
		print("MQTT server connected with succes")
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
		if splittedString[1] == "PAD_SP":
			if splittedString[0] == "PLAYERNUMBER=1":
				Racket1.update_velocity()
			elif splittedString[0] == "PLAYERNUMBER=2":
				Racket2.update_velocity()
def publish_hello(message):
	client.publish(hello_topic, message)
	print("Controller hello message send")

def end_game():
	print("Game has ended")
	client.publish(state_topic, "GAME_END")


client.on_connect = on_connect
client.on_message = on_message
client.connect("213.119.34.109", 1888, 60)
client.subscribe([(hello_topic,0),(racket_topic,0),(control_topic,0)])
ball_topic, racket_topic, control_topic
client.loop_start()
while ball_flag == 0:
	print("Game ready")
while ball_flag == 1:
	time.sleep(0.1)
	if end_game_flag == False:
		Ball.update_position()
	elif end_game_flag == True:
		end_game()