import RPi.GPIO as GPIO
import dht11 
import time
import datetime
import paho.mqtt.client
import json
import asyncio
import ssl

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# Mqtt Define      # add
AWSIoT_ENDPOINT = "a3ufrbqbd4cwta-ats.iot.ap-northeast-1.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC_PUB = "topicAirCondition"
MQTT_TOPIC_SUB = "topicAirConditionSub"
MQTT_ROOTCA = "/home/pi/Downloads/AmazonRootCA1.pem"
MQTT_CERT = "/home/pi/Downloads/069c247f064695551071b790ca00324f12e9b35ba2906d0885b9524f84899c3e-certificate.pem.crt"
MQTT_PRIKEY = "/home/pi/Downloads/069c247f064695551071b790ca00324f12e9b35ba2906d0885b9524f84899c3e-private.pem.key"

# read data using pin 14
instance = dht11.DHT11(pin=14)

def mqtt_connect(client, userdata, flags, respons_code):
    print('mqtt connected.') 
    # Entry Mqtt Subscribe.
    client.subscribe(MQTT_TOPIC_SUB)
    print('subscribe topic : ' + MQTT_TOPIC_SUB) 

def mqtt_message(client, userdata, msg):
    # Get Received Json Data 
    json_dict = json.loads(msg.payload)
    # if use ... json_dict['xxx']

# Publish Loop
async def pub_loop():
    temp_val=0
    humi_val=0
    while True:
        tm = datetime.datetime.now()
        tmstr = "{0:%Y-%m-%d %H:%M:%S}".format(tm)
        result = instance.read()
        if result.is_valid():
            temp_val = result.temperature
            humi_val = result.humidity

        print("datetime:" + tmstr + " Temperature: %-3.1f C" % temp_val + " Humidity: %-3.1f %%" % humi_val)

		# create message
        json_msg = json.dumps({"GetDateTime": tmstr, "Temperature": temp_val,"Humidity":humi_val})

		# mqtt Publish
        client.publish(MQTT_TOPIC_PUB ,json_msg)

        time.sleep(60)

# Main Procedure
if __name__ == '__main__':
    # Mqtt Client Initialize
    client = paho.mqtt.client.Client()
    client.on_connect = mqtt_connect
    client.on_message = mqtt_message
    client.tls_set(MQTT_ROOTCA, certfile=MQTT_CERT, keyfile=MQTT_PRIKEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

    # Connect To Mqtt Broker(aws)
    client.connect(AWSIoT_ENDPOINT, port=MQTT_PORT, keepalive=60)

    # Start Mqtt Subscribe 
    client.loop_start()

    # Start Publish Loop 
    loop = asyncio.get_event_loop()
    loop.run_until_complete(pub_loop())
