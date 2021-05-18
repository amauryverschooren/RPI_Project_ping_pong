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
topicHello = "setup/hello"
player = 0
controller = "Controller_B"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


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
    client.publish(topicHello, "ID="+ controller)

def on_message(client, userdata, msg):
    global player
    msg.payload = msg.payload.decode("utf-8")
    payload = str(msg.payload)
    print("Message: " + payload+"\n")

    x = payload.split("; ")
    print(x)
    if "ID="+controller in x:
        print("same as controller")
        for item in x:

            if "CONTROLLERNUMBER" in item:
                item = slice(19,20)
                player = item
    print(player)
    print("done")

client = mqtt.Client(client_id="clientId-GRysPI2021", clean_session=True, userdata=None, protocol=mqtt.MQTTv31, transport="tcp")   
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("213.119.34.109", 1888)

client.subscribe(topicHello)

helloMessage()

try:
	client.loop_forever()

except KeyboardInterrupt:
	GPIO.cleanup()

GPIO.cleanup()
