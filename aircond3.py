import RPi.GPIO as GPIO
import dht11 
import time
import datetime
import paho.mqtt.client
import json
import asyncio
import ssl
import board
import adafruit_ccs811
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image , ImageDraw ,ImageFont

i2c = board.I2C()
FONT_SANS_12 = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc" ,12)
FONT_SANS_18 = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc" ,18)

ccs811 = adafruit_ccs811.CCS811(i2c)
display = SSD1306_I2C(128, 64, board.I2C(), addr=0x3C)

while not ccs811.data_ready:
    pass

display.fill(0)
display.show()

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

# Main Loop
async def main_loop():

    # Value Initialize
    eco2 = 0
    tvoc = 0
    temp = 0
    humi = 0
    counter = 1
    next_send_tm = datetime.datetime.now()
    next_disp_tm = datetime.datetime.now()

    while True:
        # DateTime Get.
        tm = datetime.datetime.now()

        # CSS811 Read.
        if ccs811.data_ready:
            eco2 = ccs811.eco2
            tvoc = ccs811.tvoc

        # DHT11 Read.
        result = instance.read()
        if result.is_valid():
            temp = result.temperature
            humi = result.humidity

        # Display Drawing
        if tm >= next_disp_tm:
            img = Image.new("1",(display.width, display.height))
            draw = ImageDraw.Draw(img)
            draw.text((0,0),'時刻  ' + tm.strftime('%H:%M:%S'),font=FONT_SANS_12,fill=1)
            draw.text((0,16),'温度 {0:.1f}℃ 湿度 {1:.1f}%'.format(float(temp) ,float(humi)) ,font=FONT_SANS_12,fill=1)
            draw.text((0,32),'CO2 ' + '{:4}'.format(eco2) + ' PPM',font=FONT_SANS_12,fill=1)
            draw.text((0,48),'TVOC ' + '{:4}'.format(tvoc) + ' PPB' ,font=FONT_SANS_12,fill=1)
            display.image(img)
            display.show()

            # Debug Print.
            tmstr = "{0:%Y-%m-%d %H:%M:%S}".format(tm)
            print("dt:" + tmstr + " Temp: %-3.1f C" % temp + " Humi: %-3.1f %%" % humi + " CO2: %d PPM" % eco2 + " TVOC: %d PPB" % tvoc )

            # set next display time
            next_disp_tm = tm + datetime.timedelta(seconds=1)

        # Publish MQTT once a minute
        if tm >= next_send_tm:
            print("sent mqtt")
            # Message Created.
            json_msg = json.dumps({"GetDateTime": tmstr, "Temperature": temp,"Humidity":humi,"CO2":eco2,"TVOC":tvoc})
            # mqtt Publish
            #client.publish(MQTT_TOPIC_PUB ,json_msg)
            # set next mqtt time
            next_send_tm = tm + datetime.timedelta(minutes=1)

        time.sleep(0.1)

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

    # Start Loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())

