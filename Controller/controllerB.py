
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

#leds
ledList = [4, 27, 17]

#buttons
buttonList = [18, 23, 24]

# players
player_score = [0,0]

#flag
flag = False
winnerPlayer = ""
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
        self.button = tk.Button(self.parent, text="start game", command=self.buttonClick)
        self.button.pack()
    
    def destroySplash(self):
        self.parent.destroy()
        self.parent.quit()
        # startUI()
        # Game(tk.Tk())

    def buttonClick(self):
        startGame()

#strings
topics = ["setup/hello", "game/controller", "game/racket", "game/ball", "game/state", "game/score", "game/led"]
player = 0
controller = "Controller_B"

root = tk.Tk()
splash = splash(root)

def upButton(channel):
    client.publish(topics[1], "PLAYERNUMBER=" + str(player)+ "; PAD_UP")

def downButton(channel):
    client.publish(topics[1], "PLAYERNUMBER=" + str(player)+ "; PAD_DN")

def middleButton(channel):
    client.publish(topics[1], "PLAYERNUMBER=" + str(player)+ "; PAD_SP" )

def helloMessage():
    client.publish(topics[0], "ID=" + controller)

def startGame():
    client.publish(topics[4], "CONTROLLER=GAME_STARTED" )

class Bar():
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        
        self.id = self.canvas.create_rectangle(0, 0, 10 , 100, fill='white')
        # self.canvas.coords(self.id , x, y)
        self.update(y)

    def update(self, y):
        self.y = y
        # self.move()

    def move(self):
        self.canvas.coords(self.id, self.x, self.y, self.x+ 10, self.y+100)
              
class Ball():
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.id = self.canvas.create_oval(0 , 0, 20, 20, fill='white')
        self.update(x,y)
    
    def update(self, x, y):
        self.x = x
        self.y = y
        # self.move()

    def move(self):
        self.canvas.coords(self.id, self.x, self.y, self.x + 20, self.y+ 20)
        
def enableButtonEvents():
    print("buttons enabled")
    GPIO.add_event_detect(18, GPIO.FALLING, callback=upButton, bouncetime=150)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=downButton, bouncetime=150)
    GPIO.add_event_detect(24, GPIO.FALLING, callback=middleButton, bouncetime=150)

def startUI():
    global bar1,bar2, ball , canvas, score_Player_1, score_Player_2, rootgame, winner
    rootgame= tk.Tk()
    rootgame.title("Ping Pong")
    canvas = tk.Canvas(rootgame, width=600, height=400, bg='#000000')
    canvas.pack()
    rootgame.update()

    middle = canvas.create_rectangle(298.5 , 0, 298.5+ 3, 600, width=2, fill='#222222')

    bar1 = Bar(canvas, 20, 175)
    bar2 = Bar(canvas, 565, 175)

    ball = Ball(canvas, 290, 190 )

    score_Player_1 = canvas.create_text(200,24, anchor="center", fill="#ffffff", text="Player 1: "+ str(player_score[0]) )
    score_Player_2 = canvas.create_text(400,24, anchor="center", fill="#ffffff", text="Player 2: "+ str(player_score[1]))
    winner = canvas.create_text(300, 200, anchor="center", fill="#ffffff", text="" )
    enableButtonEvents()
    time.sleep(1)
    # main()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_publish(client, userdata, msg):
    print("")

def on_subscribe(client, userdata, msg, granted_qos):
    print("Subscribed: " + str(msg) + " QoS: " + str(granted_qos))

def on_message(client, userdata, msg):
    global player, bar1, bar2, ball, Upper_left, Upper_right, flag, winnerPlayer
    msg.payload = msg.payload.decode("utf-8")
    payload = str(msg.payload)
    # print("Message: " + payload + "\n")

    x = payload.split("; ")
    print(x)

    # hello
    if msg.topic == topics[0]:

        if "ID=" + controller in x:
        # print("same as controller")
            for item in x:

                if "PLAYERNUMBER" in item:
                    player = item[slice(13, 14)]
                    print(player)
                    turnPlayerLedOn(int(player))

    # controller
    elif msg.topic == topics[1]:
        time.sleep(0)
        # print("test topic game/controller")

    # racket
    elif msg.topic == topics[2]:
        print("test topic game/racket")
        racket = x[0][slice(7,8)]
        y = x[1][9:]
    
        if int(racket) == 1: 
            bar1.update(float(y))
        elif int(racket) == 2:
            bar2.update(float(y))
        
    # ball
    elif msg.topic == topics[3]:
        # print("test topic game/ball")
        ball.update(float(x[0]), float(x[1]))

    # start
    elif msg.topic == topics[4]:
        print("test topic game/state")
        if(x[0]) == "CONTROLLER=GAME_STARTED":
            print("led")
            splash.destroySplash()
            ledTiming()

        elif(x[0] == "GAME_STARTED"):
            # startUI()
            time.sleep(0)
        elif(x[0] == "GAME_END"):
            print("end")
            winnerPlayer = x[1].replace("_", " ")
            flag = True
        
        elif(x[0] == "NEW_ROUND"):
            print("led")
            ledTiming()
            
    # score
    elif msg.topic == topics[5]:
        print("test topic game/score")
        p = x[0][slice(7,8)]
        print(p)
        score = x[1][6:]
        print(score)

        player_score[int(p)-1] = score
        print(player_score)

    # led
    elif msg.topic == topics[6]:
        print("test topic game/score")
        if x[0] == "LED_ON":
            GPIO.output(ledList[0], True )
        elif x[0] == "LED_OFF":
            GPIO.output(ledList[0], False )

def ledTiming():
    for i in range(3):
        GPIO.output(ledList[2], True)
        print("led on")
        time.sleep(1)
        GPIO.output(ledList[2], False)
        print("led off")
        time.sleep(1)

def showWON(string):
    global canvas
    canvas.create_text(300, 200, anchor="center", fill="#ffffff", text=string)

def turnPlayerLedOn(player):
    print(str(ledList[player - 1]) + " turns on")
    GPIO.output(ledList[player - 1], True)

def main():
    global score_Player_1, score_Player_2, rootgame, flag, winnerPlayer, winner
    while 1: 
        if flag == True:
            canvas.delete(winner)
            winner = canvas.create_text(300, 150, anchor="center", fill="#ffffff", text=str(winnerPlayer) + " won!" )
            

        canvas.delete(score_Player_1)
        canvas.delete(score_Player_2)
        score_Player_1 = canvas.create_text(200,24, anchor="center", fill="#ffffff", text="Player 1: "+ str(player_score[0]) )
        score_Player_2 = canvas.create_text(400,24, anchor="center", fill="#ffffff", text="Player 2: "+ str(player_score[1]))
        rootgame.update()
        ball.move()
        bar1.move()
        bar2.move()
        time.sleep(0.2)

client = mqtt.Client(client_id="clientId-nSlrniNHmL",
                     clean_session=True,
                     userdata=None,
                     protocol=mqtt.MQTTv31,
                     transport="tcp")

client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("213.119.34.109", 1888)

for topic in topics:
    client.subscribe(topic)

helloMessage()

try:
    client.loop_start()
    startUI()
    root.mainloop()
    print("try")
    main()

except KeyboardInterrupt:
    root.stop()
    GPIO.cleanup()
GPIO.cleanup()
