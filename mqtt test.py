import paho.mqtt.client as mqtt
import time

def mqtt_on_message(mqtt_client, userdata, message):
    """Empfängt MQTT Payloads und trägt sie ins Dict ein"""
    mqtt_subscribes[message.topic] = str(message.payload.decode("utf-8"))


def mqtt_on_connect(mqtt_client, userdata, flags, rc):
    for topic in mqtt_subscribes:
        mqtt_client.subscribe(topic)
    

mqtt_client = mqtt.Client()
mqtt_client.on_connect = mqtt_on_connect
mqtt_client.on_message = mqtt_on_message
mqtt_client.connect('192.168.178.240')
mqtt_client.loop_start()

mqtt_subscribes = dict([
    ('/test', 'test'),
    ('/test2', None)
])

while True:
    print (mqtt_subscribes['/test'])
    print (mqtt_subscribes['/test2'])


    time.sleep(1)