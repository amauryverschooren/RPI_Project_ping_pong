#!/usr/bin/env python3

from tkinter.constants import BOTTOM
from typing import Text
from threading import Thread
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import tkinter as tk
import sys
import os

import time

GPIO.setmode(GPIO.BCM)

#leds
ledList = [4, 27, 17]

#buttons
buttonList = [18, 23, 24]

#setup
for i in range(len(ledList)):
    GPIO.setup(ledList[i], GPIO.OUT)
    GPIO.output(ledList[i], False)

for i in range(len(buttonList)):
    GPIO.setup(buttonList[i], GPIO.IN,  pull_up_down=GPIO.PUD_UP)

#check if terminal or screen
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

#strings
topics = ["setup/hello", "game/controller", "game/racket", "game/ball", "game/start"]
player = 0
controller = "Controller_B"

def upButton(channel):
    client.publish(topics[1], "PLAYERNUMBER=" + str(player)+ "; PAD_UP")

def downButton(channel):
    client.publish(topics[1], "PLAYERNUMBER=" + str(player)+ "; PAD_DN")

def middleButton(channel):
    client.publish(topics[1], "PLAYERNUMBER=" + str(player)+ "; PAD_SP" )

class Bar():
    def __init__(self, canvas, x, y):
        #threading.Thread.__init__(self)
        self.canvas = canvas
        self.x = x
        
        self.id = self.canvas.create_rectangle(0, 0, 10 , 100, fill='white')
        # self.canvas.coords(self.id , x, y)
        self.update(y)

    def update(self, y):
       #threading.Thread.update(self)
        self.y = y
        # self.move()

    def move(self):
        self.canvas.coords(self.id, self.x, self.y, self.x+ 10, self.y+100)

    def bar_to_be_threaded():
        threading.Thread(target=self.move).start()
        
class Ball():
    def __init__(self, canvas, x, y):
        #threading.Thread.__init__(self)
        self.canvas = canvas
        self.id = self.canvas.create_oval(0 , 0, 20, 20, fill='white')
        self.update(x,y)
    
    def update(self, x, y):
        #threading.Thread.update(self)
        self.x = x
        self.y = y
        # self.move()

    def move(self):
        self.canvas.coords(self.id, self.x, self.y, self.x + 20, self.y+ 20)

    def ball_to_be_threaded():
        threading.Thread(target=self.move).start()
        
def enableButtonEvents():
    print("buttons enabled")
    GPIO.add_event_detect(18, GPIO.FALLING, callback=upButton, bouncetime=150)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=downButton, bouncetime=150)
    GPIO.add_event_detect(24, GPIO.FALLING, callback=middleButton, bouncetime=150)

root= tk.Tk()
root.title("Ping Pong")
canvas = tk.Canvas(root, width=600, height=400, bg='#000000')
canvas.pack()
root.update()

middle = canvas.create_rectangle(298.5 , 0, 298.5+ 3, 600, width=2, fill='#222222')

bar1 = Bar(canvas, 20, 175)
bar2 = Bar(canvas, 565, 175)

ball = Ball(canvas, 290, 190 )

enableButtonEvents()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    for topic in topics:
        client.subscribe(topic)

    helloMessage()

def on_publish(client, userdata, msg):
    print("")

def on_subscribe(client, userdata, msg, granted_qos):
    print("Subscribed: " + str(msg) + " QoS: " + str(granted_qos))

def helloMessage():
    client.publish(topics[0], "ID=" + controller)

def startGame():
    client.publish(topics[4], "GAME_START" )

def on_message(client, userdata, msg):
    global player, bar1, bar2, ball
    msg.payload = msg.payload.decode("utf-8")
    payload = str(msg.payload)
    print("Message: " + payload + "\n")

    x = payload.split("; ")
    print(x)

    if msg.topic == topics[0]:

        if "ID=" + controller in x:
        # print("same as controller")
            for item in x:

                if "PLAYERNUMBER" in item:
                    player = item[slice(13, 14)]
                    print(player)
                    turnPlayerLedOn(int(player))


    elif msg.topic == "game/controller":
        print("test topic game/controller")

    elif msg.topic == "game/racket":

        print("test topic game/racket")
        racket = x[0][slice(7,8)]
        print(racket)
        y = x[1][9:]
    
        print(y)

        if int(racket) == 1: 
            print("racket1")
            bar1.update(float(y))
        elif int(racket) == 2:
            print("racket2")
            bar2.update(float(y))

        # ["bar"+ racket].update(y)
        

    elif msg.topic == "game/ball":
        print("test topic game/ball")

        ball.update(float(x[0]), float(x[1]))


    elif msg.topic == "game/start":
        print("test topic game/start")
        startUI()

def turnPlayerLedOn(player):
    print(str(ledList[player - 1]) + " turns on")
    GPIO.output(ledList[player - 1], True)

class splash(tk.Frame):
    def __init__(self, parent):
        threading.Thread.__init__(self)
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
        # self.parent.destroy()
        startGame()
        # Game(tk.Tk())

    def spash_to_be_threaded():
        threading.Thread(target=self.makeSplash).start()
        threading.Thread(target=self.destroySplash).start()


def main():

    while 1: 
        root.update()
        ball.move()
        bar1.move()
        bar2.move()
        time.sleep(0.1)
    # Lower_left = canvas.Label(root,text ='Player 1')
    # Upper_right = canvas.Label(root,text ='Player 2')
        
    # Lower_left.place(relx = 0.0, rely = 0.0,anchor ='nw')
    # Upper_right.place(relx = 1.0,rely = 0.0,anchor ='ne')
    enableButtonEvents()



class Game(tk.Frame):
    def __init__(self,root):
        threading.Thread.__init__(self)
        tk.Frame.__init__(self,root) 
        self.root = root
        self.createGame()
        self.enableButtonEvents()
    
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



    def enableButtonEvents(self):
        print("buttons enabled")
        GPIO.add_event_detect(18, GPIO.FALLING, callback=upButton, bouncetime=250)
        GPIO.add_event_detect(23, GPIO.FALLING, callback=downButton, bouncetime=250)
        GPIO.add_event_detect(24, GPIO.FALLING, callback=middleButton, bouncetime=250)

    def game_to_be_threaded(self):
        #threading.Thread(target=__init__, self, root)
        threading.Thread(target=self.createGame).start()
        threading.Thread(target=self.enableButtonEvents).start()

# class drawing:
    # @abstractmethod
    # def update(self, x,y):
    #     pass

    # @abstractmethod
    # def create(self):
    #     pass




client = mqtt.Client(client_id="clientId-b0p5xkpzF5",
                     clean_session=True,
                     userdata=None,
                     protocol=mqtt.MQTTv31,
                     transport="tcp")

client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("213.119.34.109", 1888)

job1 = Thread(target=helloMessage)
job2 = Thread(target=startGame)
#job3 = Thread(target=player.createGame).start()
#job4 = Thread(target=enableButtonEvents)
#job5 = Thread(target=upButton,args=(channel))
#job6 = Thread(target=downButton,args=(channel))
#job7 = Thread(target=middleButton,args=(channel))
#job8 = Thread(target=main)

job1.start()
job2.start()
#job3.start()
#job4.start()
#job5.start()
#job6.start()
#job7.start()
#job8.start()

# createMainGame()
# root = tk.Tk()
# splash(root)
# Game(root)


# GPIO.add_event_detect(18, GPIO.RISING, callback=increaseLedMsg, bouncetime=250)
# GPIO.add_event_detect(24, GPIO.RISING, callback=decreaseLedMsg, bouncetime=250)


try:
    client.loop_start()
    main()

    # root.mainloop()
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()
