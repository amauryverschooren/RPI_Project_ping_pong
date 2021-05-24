#!/usr/bin/env python3

from tkinter.constants import BOTTOM
from typing import Text
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import tkinter as tk
import sys
import os

import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.OUT)

#leds
ledList = [4, 27, 17]

#buttons
buttonList = [18, 23, 24]



#setup
for i in range(len(ledList)):
    GPIO.setup(ledList[i], GPIO.OUT)
    GPIO.output(ledList[i], False)

for i in range(len(buttonList)):
    GPIO.setup(buttonList[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#strings
topic = "game/controller"
topicHello = "setup/hello"

player = 0
controller = "Controller_A"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def on_publish(client, userdata, msg):
    print("Message published")


def on_subscribe(client, userdata, msg, granted_qos):
    print("Subscribed: " + str(msg) + " QoS: " + str(granted_qos))


def upButton(channel):
    client.publish(topic, "VAR=UP; CONTROLLER=" + player)


def downButton(channel):
    client.publish(topic, "VAR=DN; CONTROLLER=" + player)


def middleButton(channel):
    client.publish(topic, "VAR=SP; CONTROLLER=" + player)


def helloMessage():
    client.publish(topicHello, "ID=" + controller)

def startGame():
    client.publish(gameStartTopic, )


def on_message(client, userdata, msg):
    global player
    msg.payload = msg.payload.decode("utf-8")
    payload = str(msg.payload)
    print("Message: " + payload + "\n")

    x = payload.split("; ")
    print(x)
    if "ID=" + controller in x:
        # print("same as controller")
        for item in x:

            if "PLAYERNUMBER" in item:
                player = item[slice(13, 14)]
                print(player)
                turnPlayerLedOn(int(player))

    print("done")


def turnPlayerLedOn(player):
    print(str(ledList[player - 1]) + " turns on")

    GPIO.output(ledList[player - 1], True)


client = mqtt.Client(client_id="clientId-GrysPI2021",
                     clean_session=True,
                     userdata=None,
                     protocol=mqtt.MQTTv31,
                     transport="tcp")

client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("213.119.34.109", 1888)

client.subscribe(topicHello)

helloMessage()

#check if terminal or screen
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

class splash(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        self.makeSplash()
        # SPLASH SCREEN

    def makeSplash(self):
        # splash_root = tk.Tk()
        self.parent.geometry("200x200")
        self.parent.title("Splash")
        self.label = tk.Label(self.parent, text="Welcome", font=18)
        self.label.pack()
        self.button = tk.Button(self.parent, text="start game", command=self.destroySplash)
        self.button.pack()
    
    def destroySplash(self):
        self.parent.destroy()
        # startGame()
        # Game(tk.Tk())

class Game(tk.Frame):
    def __init__(self,root):
        tk.Frame.__init__(self,root) 
        self.root = root
        self.createGame()       


    def createGame(self):

        self.root.title("Ping Pong")

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.canvas = tk.Canvas(self.frame, width=600, height=400, bg='#000000')
        self.canvas.pack()

        self.bar1 = Bar(self.canvas, 20, 175)
        self.bar2 = Bar(self.canvas, 565, 175)

        self.middle = self.canvas.create_rectangle(298.5 , 0, 298.5+ 3, 600, width=2, fill='#222222')

        self.ball = Ball(self.canvas, 290, 190 )

        self.Lower_left = tk.Label(root,text ='Player 1')
        self.Upper_right = tk.Label(root,text ='Player 2')
        
        self.Lower_left.place(relx = 0.0, rely = 0.0,anchor ='nw')
        self.Upper_right.place(relx = 1.0,rely = 0.0,anchor ='ne')

class Bar():
    def __init__(self, canvas, x, y):
        self.y = y
        self.x = x
        self.canvas = canvas
        self.canvas.create_rectangle(self.x , self.y, self.x + 15, self.y +85, width=2, fill='white')

    def update(self, canvas, x, y):
        time.sleep(0.1)
        
class Ball():
    def __init__(self, canvas, x, y):
        self.y = y
        self.x = x
        self.canvas = canvas
        self.canvas.create_oval(self.x , self.y, self.x + 20, self.y +20, width=2, fill='white')


# createMainGame()
root = tk.Tk()
# splash(root)
Game(root)


# GPIO.add_event_detect(18, GPIO.RISING, callback=increaseLedMsg, bouncetime=250)
# GPIO.add_event_detect(24, GPIO.RISING, callback=decreaseLedMsg, bouncetime=250)

try:
    client.loop_start()
    root.mainloop()
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()
