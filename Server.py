from fastapi import FastAPI, Form
import uvicorn
from time import strftime
from pydantic import BaseModel
import pymongo
import paho.mqtt.client as mqtt 
import json
from typing import Dict,Union

app = FastAPI()

myclient = pymongo.MongoClient(
    "mongodb+srv://iuhbuoi10:iuhbuoi10@b10mqtt.kfgbma5.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["mydatabase"]
mycol = mydb["ras1"]
mycol2 =mydb["ras2"]


def on_connect(client, userdata, flags, rc):
    print('Connected with result code {}'.format(rc))

def on_disconnect(client, userdata, rc):
    print('Disconnected')

def connect_to_mqtt_server():
    client = mqtt.Client("linh")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(username="device1", password="device1")
    client.connect("192.168.1.101",1883,60)

class Item(BaseModel):
    Humi: float | None = None
    Temp: float | None = None
    Led1: float |None =None
    Led2: float |None=None
    lcd  : str   |None=None
    thumb: float 
    servo: float |None=None
    light: float | None =None

class Item2(BaseModel):
    Ultra: float |None=None
    relay: float |None=None

############# RAS 1 ############### HTTP

@app.post("/data_all")
async def data_post(item: Item):

    client = mqtt.Client("linh")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(username="device1", password="device1")
    client.connect("192.168.1.101",1883,60)

                   
    currentime = strftime("%H:%M:%S")
    dem = mycol.count_documents({})
    dem += 1
    mydict = {
        "_id": dem,
        "Time": currentime,
        "Device": "THINKPAD_JSON",
        "Humi": item.Humi,
        "Temp": item.Temp,
        "Led1":item.Led1,
        "Led2":item.Led2,
        "lcd":item.lcd,
        "thumb":item.thumb,
        "servo":item.servo,
        "light":item.light
    }
    print(mydict)
    mycol.insert_one(mydict)
    
    params = json.dumps(mydict).encode()
    client.publish("ras1_all_http", params)
    return {"Publish_Successfully"}
################ RAS 2 ####################### MQTT

@app.post("/data_ras2_all")
async def data_post2(item: Item2):            
    currentime = strftime("%H:%M:%S")
    dem = mycol2.count_documents({})
    dem += 1
    mydict = {
        "_id": dem,
        "Time": currentime,
        "Device": "THINKPAD_RAS2",
        "Ultra" : item.Ultra,
        "relay" : item.relay
    }
    print(mydict)
    mycol2.insert_one(mydict)
    return {"rass2_publish_Successfully"}

################### GET ####################
@app.get("/get_all_data_ras1", response_model=Dict[str, Union[int, str]])
async def get_data_from_database():
    mydoc = list(mycol.find().sort("_id", -1))
    if mydoc:
        return mydoc[0]
    else:
        print("Not data")
##################### GET HUMI ras1 ###############
@app.get("/get_data_humi_ras1", response_model=float)
async def get_data_from_database():
    mydoc = mycol.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['Humi']
    else:
        print("not data")

@app.get("/get_data_temp_ras1", response_model=float)
async def get_data_from_database():
    mydoc = mycol.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['Temp']
    else:
        print("not data")

@app.get("/get_data_Led1_ras1", response_model=float)
async def get_data_from_database():
    mydoc = mycol.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['Led1']
    else:
        print("not data")

@app.get("/get_data_Led2_ras1", response_model=float)
async def get_data_from_database():
    mydoc = mycol.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['Led2']
    else:
        print("not data")

@app.get("/get_data_lcd_ras1", response_model=str)
async def get_data_from_database():
    mydoc = mycol.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['lcd']
    else:
        print("not data")

@app.get("/get_data_servo_ras1", response_model=float)
async def get_data_from_database():
    mydoc = mycol.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['servo']
    else:
        print("not data") 

@app.get("/get_data_light_ras1", response_model=float)
async def get_data_from_database():
    mydoc = mycol.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['light']
    else:
        print("not data")  

################### GET DATA RAS2 ###############
@app.get("/get_all_data_ras2", response_model=Dict[str, Union[int, str]])
async def get_data_from_database():
    mydoc = list(mycol2.find().sort("_id", -1))
    if mydoc:
        return mydoc[0]
    else:
        print("Not data")
##### ultra #####       
@app.get("/get_data_ultra_ras2", response_model=float)
async def get_data_from_database():
    mydoc = mycol2.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['ultra']
    else:
        print("not data")
########### relay ###
@app.get("/get_data_relay_ras2", response_model=float)
async def get_data_from_database():
    mydoc = mycol2.find().sort("_id", -1)
    if mydoc:
        return mydoc[0]['relay']
    else:
        print("not data")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
