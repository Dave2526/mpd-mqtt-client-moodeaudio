'''
Helper Program to switch a GPIO at Play on and at Stop off,
Share State, Album and Title via MQTT 
Recieve Play/ Pause via MQTT

Switch in MoOde Config / System Config / Local Services / LCD update engine on, 
otherwise the currentsong.txt is not written (original for LCD Displays)

install depencies with 
       sudo pip install paho-mqtt
       sudo pip install python-mpd2
and run it via a service (Name: control)

Written by Dave2526 on 2022-04
'''

from mpd import MPDClient
import time, requests
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

# Pin where Speaker is connected (GPIO.BCM, GPIO Number)
speaker = 21
# MQTT Topic
mqtt_topic = '/kueche/radio'


# Definations
def mqtt_on_connect(mqtt_client, userdata, flags, rc):
    print ('MQTT verbunden')
    mqtt_client.publish(mqtt_topic+"/lwt", "Online")
    mqtt_client.subscribe(mqtt_topic+'/cmd/power')
    mqtt_client.publish(mqtt_topic+'/state/album', ' ')
    mqtt_client.publish(mqtt_topic+'/state/title', ' ')


def mqtt_on_message(mqtt_client, userdata, message):
    #mqtt_subscribes[message.topic] = str(message.payload.decode("utf-8"))
    topic = str(message.topic)
    payload = str(message.payload.decode("utf-8"))
    if topic == mqtt_topic+'/cmd/power':
        if payload == 'play':
            requests.get('http://localhost/command/?cmd=play')
        elif payload == 'stop':
            mpd_client.play()
            requests.get('http://localhost/command/?cmd=stop')



# initialize MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = mqtt_on_connect
mqtt_client.on_message = mqtt_on_message
mqtt_client.will_set(mqtt_topic+'/lwt', 'Offline', retain=True)
mqtt_client.connect('192.168.178.240')
mqtt_client.loop_start()


# initialize the MPD client
mpd_client = MPDClient()               # create client object
mpd_client.timeout = 10                # network timeout in seconds (floats allowed)
mpd_client.connect("localhost", 6600)  # connect to localhost:6600

# initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(speaker, GPIO.OUT)
GPIO.output(speaker, GPIO.HIGH)     # Off, inverted   
speaker_on = False

state = 'stop'
album = ''
l_album = ''
title = ''
l_title = ''

################
# Main Program #
################
while True:
    # Get state direct from mpd
    try:
        status = mpd_client.status()
        state = status['state']
    except:
        time.wait(2)
        mpd_client.connect("localhost", 6600)
    
    # switch speakers and publish via MQTT
    if state == 'play' and speaker_on == False:
        GPIO.output(speaker, GPIO.LOW)     # On, inverted 
        speaker_on = True
        mqtt_client.publish(mqtt_topic+'/state/power', 'Play')
    elif state != 'play' and speaker_on == True:
        GPIO.output(speaker, GPIO.HIGH)     # Off, inverted 
        speaker_on = False
        mqtt_client.publish(mqtt_topic+'/state/power', 'Stop')
        mqtt_client.publish(mqtt_topic+'/state/album', ' ')
        mqtt_client.publish(mqtt_topic+'/state/title', ' ')
        l_album = ''
        l_title = ''

    # read title and album from MoOde
    try:
        with open("/var/local/www/currentsong.txt") as file1:
            for line in file1:
                if 'album' in line:
                    album = line.split('=', 1)[1]
                elif 'title' in line:
                    title = line.split('=', 1)[1]
    except:
        album = 'File not readable'
        title = 'File not readable'
        
    # if radio is playing and items changed, publish via MQTT
    if state == 'play':
        if l_album != album:
            mqtt_client.publish(mqtt_topic+'/state/album', str(album))
            l_album = album
        elif l_title != title:
            mqtt_client.publish(mqtt_topic+'/state/album', str(album))
            mqtt_client.publish(mqtt_topic+'/state/title', str(title))
            l_title = title

    
    time.sleep(0.2)