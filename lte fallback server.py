import subprocess, urllib.request, time
import paho.mqtt.client as mqtt


conn = "WLAN"
ping_state = ""
ping_counter = 0
mqtt_topic ="/server/ltefallback/state"


def ping(host):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False

def wlan_verb():
    if "wlan0" in subprocess.check_output(['cat','/proc/net/wireless'],universal_newlines=True):
        return True
    else:
        return False



mqtt_client = mqtt.Client()
mqtt_client.connect('localhost')
mqtt_client.loop_start()

while True:
    wlan_ok = wlan_verb()
    ping_state = ping("google.de")
    # WLan verbunden, alles OK
    if wlan_ok == True and ping_state == True and conn == "LTE":
        conn = "WLAN"
        ping_counter = 0
        mqtt_client.publish(mqtt_topic, conn)
        # LTE trennen
        try:
            subprocess.check_output(['sudo','killall','wvdial'],universal_newlines=True, timeout=3)
        except:
            pass
        time.sleep(4)

    # Bei Ausfall umschalten auf LTE
    elif (wlan_ok == False or ping_state == False) and conn == "WLAN":
        ping_counter +=1
        if ping_counter >= 4:
            try:
                subprocess.check_output(['sudo','wvdial'],universal_newlines=True, timeout=5)
            except:
                pass
            ping_counter = 0
            conn = "LTE"
            mqtt_client.publish(mqtt_topic, conn)

    time.sleep(20)    
