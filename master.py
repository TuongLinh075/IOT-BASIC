import socket
import ast
import paho.mqtt.client as mqtt
from time import sleep
import json
from urllib.request import Request, urlopen
from seeed_dht import DHT
from grove.grove_ryb_led_button import GroveLedButton
from grove.display.jhd1802 import JHD1802
from grove.grove_servo import GroveServo
from grove.grove_light_sensor_v1_2 import GroveLightSensor
from grove.grove_thumb_joystick import GroveThumbJoystick

dht = DHT('11', 5)
led1 = GroveLedButton(22)
led2 = GroveLedButton(24)
lcd = JHD1802()
servo = GroveServo(12)
sensor = GroveLightSensor(0)
sensor1 = GroveThumbJoystick(2)

localIP = "0.0.0.0"
localPort = 11000
bufferSize = 1024

UDP_Server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDP_Server.bind((localIP, localPort))
print("UDP server up and listening")

relay_value = 0
led1_value = 0
led2_value =0 
servo_value=0

def processReceived(dataReceived):
    input_string = dataReceived.decode("utf-8")
    data_dict = ast.literal_eval(input_string)
    return data_dict

def framePacking(start, id, cmd, data, stop):
    data_dict = {
        "Start": start,
        "ID": id,
        "CMD": cmd,
        "Length": len(data),
        "Data": data,
        "Stop": stop
    }
    return data_dict

def on_connect(client, userdata, flags, rc):
    print("Connected with result code {rc}")
    if rc==0:
        client.subscribe("nhan_Led1_control")
        client.subscribe("nhan_Led2_control")
        client.subscribe("nhan_Relay_control")
        client.subscribe("nhan_Servo_control")
        client.subscribe("nhan_Lcd_control")
    else:
        print("return code {rc}")

def on_message(client, userdata, msg):
    global led1_value, led2_value,relay_value,servo_value
    print("Received message on topic {msg.topic}: {msg.payload.decode()}")
    data = json.loads(msg.payload.decode())

    if msg.topic == 'nhan_Led1_control':
        led1_value = data.get("Led1")
        if led1_value == 1:
            led1.led.light(True)
            print("led1 on")
        if led1_value == 0:
            led1.led.light(False)
            print("led1 off")

    if msg.topic == 'nhan_Led2_control':
        led2_value = data.get("Led2")
        if led2_value == 1:
            led2.led.light(False)
            print("led2 on")
        if led2_value == 0:
            led2.led.light(False)
            print("led2 off")
    
    if msg.topic == 'nhan_Servo_control':
        servo_value = data.get("Servo")
        servo.setAngel(servo_value)
        sleep(2)

    if msg.topic == 'nhan_Lcd_control':
        text_lcd = data.get("LCD")
        lcd.setCursor(0,0)
        lcd.write(''.format(text_lcd))

    if msg.topic == 'nhan_Relay_control':
        data = json.loads(msg.payload.decode())
        relay_value = data.get('Relay')

        try:
            UDP_Server.settimeout(5)
            msgToClient = str(framePacking(0x01, 0x00, 0x01, [relay_value], 0x00))
            bytesToSend = str.encode(msgToClient)
            ClientMsg = UDP_Server.recvfrom(bufferSize)
            ClientMsg_message = ClientMsg[0]
            ClientMsg_address = ClientMsg[1]
            UDP_Server.sendto(bytesToSend, ClientMsg_address)
            sleep(5)
        except socket.timeout:
            print("Lỗi kết nối")

# gui du liêu ras1 thong qua HTTP
def post_all(data1,data2,data3,data4,data5,data6,data7,data8):
    data = {
        "Humi": data1,
        "Temp":data2,
        "Led1":data3,
        "Led2":data4,
        "lcd":data5,
        "thumb":data6, 
        "servo":data7,
        "light":data8
    }
    type_json = json.dumps(data)
    return type_json

def post_http_ras1(data1):
    url = 'http://192.168.1.34:8000/data_all'
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    try:
        req = Request(url, data=data1.encode(), headers=headers, method='POST')
        response = urlopen(req)
        response_data = response.read()
        return response_data
    except Exception as e:
        print(f"Error my_post: {str(e)}")

# posst du lieu thong qua mqtt
def Postt_dulieu():
    while True:
        global led1_value, led2_value,relay_value,servo_value
        humi, temp = dht.read()
        light = sensor.light
        thumb, y = sensor1.value
        lcd = 'linh'
        data_to_post = post_all(humi, temp, led1_value, led2_value, lcd, thumb, servo_value ,light)
        post_http_ras1(data_to_post)

        try:
            client_id='linh'
            client =mqtt.Client(client_id)
            client.on_connect=on_connect
            client.on_message=on_message
            client.username_pw_set(username='device1',password='device1')
            client.connect("192.168.1.34",1883,60)
            
            UDP_Server.settimeout(5)
            msgToClient = str(framePacking(0x01, 0x00, 0x01, [relay_value], 0x00))
            bytesToSend = str.encode(msgToClient)

            ClientMsg = UDP_Server.recvfrom(bufferSize)
            ClientMsg_message = ClientMsg[0]
            ClientMsg_address = ClientMsg[1]
            data_dict = processReceived(ClientMsg_message)

            print(data_dict)
            message = "Mesage from Client: {}".format(data_dict)
            print(message)
            
            address = "Client IP + Port: {}".format(ClientMsg_address)
            ultra_udp=data_dict['Data'][0]
            ultra_udp=float(ultra_udp)
            print("-------")
            print(type(ultra_udp))
            data = {
                        "Ultra": ultra_udp,
                        "relay" : relay_value
                    }
            json_data = json.dumps(data)
            client.publish("ras2_mq", json_data)
            print(json_data)
            UDP_Server.sendto(bytesToSend, ClientMsg_address)
            sleep(10)
        except socket.timeout:
                print("Không nhận được dữ liệu từ slave, thực hiện các công việc khác")
                
def run():
    try:
        client_id='linh'
        client =mqtt.Client(client_id)
        client.on_connect=on_connect
        client.on_message=on_message
        client.username_pw_set(username='device1',password='device1')
        client.connect("192.168.1.34",1883,60)
        client.loop_start()
        Postt_dulieu()
        sleep(10)
    except Exception as e:
        print("Lỗi:", str(e))
        sleep(10)

if __name__ == "__main__":
    run()