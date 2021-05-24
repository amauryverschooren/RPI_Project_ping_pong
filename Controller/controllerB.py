#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)

#leds
ledList = [4,17,27]

#buttons
buttonList = [18,23,24]

#setup
for i in range(len(ledList)):
    GPIO.setup(ledList[i],GPIO.OUT)
    GPIO.output(ledList[i], False)

for i in range(len(buttonList)):
    GPIO.setup(buttonList[i],GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#strings
topic = "TopicTest"
player = 0
controller = "Controller_B"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #Subscribing in de on_connect() zorgt ervoor dat bij een connectie verlies
    #en het reconnecten de subscribtie vernieuwd zal worden.
    client.subscribe("setup/hello")
    client.subscribe("game/controller")
    client.subscribe("game/racket")
    client.subscribe("game/ball")
    client.subscribe("game/start")
    helloMessage()

def on_publish(client, userdata, msg):
    print("Message published")

def on_subscribe(client, userdata, msg, granted_qos):
    print("Subscribed: " + str(msg) + " QoS: " + str(granted_qos))

def upButton(channel):
    client.publish(topic, "VAR=UP; NAAM="+ controller)

def downButton(channel):
    client.publish(topic, "VAR=DN; NAAM="+ controller)

def middleButton(channel):
    client.publish(topic, "VAR=MD; NAAM="+ controller)

def helloMessage():
    client.publish("setup/hello", "ID="+ controller)

def on_message(client, userdata, msg):
    global player
    msg.payload = msg.payload.decode("utf-8")
    payload = str(msg.payload)
    print("Message: " + payload+"\n")

    x = payload.split("; ")
    print(x)

    if msg.topic == "setup/hello":
        if "ID="+controller in x:
            print("same as controller")
            for item in x:

                if "CONTROLLERNUMBER" in item:
                    item = slice(19,20)
                    player = item
        print(player)
        print("done")

    elif msg.topic == "game/controller":
        print("test topic game/controller")

    elif msg.topic == "game/racket":
        print("test topic game/racket")

    elif msg.topic == "game/ball":
        print("test topic game/ball")

    elif msg.topic == "game/start":
        print("test topic game/start")

client = mqtt.Client(client_id="clientId-GRysPI2021", clean_session=True, userdata=None, protocol=mqtt.MQTTv31, transport="tcp")   
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("213.119.34.109", 1888, 60)

try:
	client.loop_forever()

except KeyboardInterrupt:
	GPIO.cleanup()

GPIO.cleanup()
