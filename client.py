import socket
from time import sleep
import ast
from grove.grove_relay import GroveRelay
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger

relay = GroveRelay(5)   
sensor = GroveUltrasonicRanger(16)
ServerAddressPort = ("192.168.1.101", 11000)
bufferSize = 1024

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

b = 0
while True:
    ultra = sensor.get_distance()
    print("khoang cách: ",ultra)
    msgToServer = str(framePacking(0x01, 0x01, 0x01, [ultra,b], 0x00))
    bytesToSend = str.encode(msgToServer)

    UDP_Client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDP_Client.sendto(bytesToSend, ServerAddressPort)

    ServerMsg = UDP_Client.recvfrom(bufferSize)
    ServerMsg_message = ServerMsg[0]
    ServerMsg_address = ServerMsg[1]

    message = "Message from Server: {}".format(ServerMsg_message)
    address = "Message from Server: {}".format(ServerMsg_address)
    a = ServerMsg_message
    data = processReceived(a)
    print(data)
    b = data['Data'][0]
    if b == 1:
        relay.on()
        print(" relay on")
        print(b)
    else:
        relay.off()
        print("relay off")
        print(b)

    print(message)
    print(address)
    sleep(1)