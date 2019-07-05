from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate
import configparser
from datetime import datetime
import base64
import threading
import json 
from mqttClient import MqttClient
from handleBle import BleHandler
from lineMsg import LineClient


class ConnectionHandlerThread(threading.Thread):
    def __init__(self, connection_index, devAddr):
        threading.Thread.__init__(self)
        self.connection_index = connection_index
        self.devAddr = devAddr
        print("thread index : "+str(self.connection_index))

    def run(self):
        bleHnadler=BleHandler(self.devAddr,mqttClient,lineClient)
        bleHnadler.BleConnect()


def connect(devAddr):
    t = ConnectionHandlerThread(len(connections), devAddr)
    t.start()





config = configparser.ConfigParser()
config.read('./config/config.ini')

connections = []

token = config.get('default', 'AesToken')
broker = config.get('default', 'broker')
mqttClient=MqttClient(broker)
mqttClient.init()

lineClient=LineClient(token)
lineClient.NotifyMessage("spo2 gateway start!!")
lineClient.NotifyMessage("mqtt broker address : "+broker)

scanner =Scanner(0)
devices=scanner.scan(10.0)
print("scaning")

addresses=[]
for dev in devices:
    print ("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
                    # print ("  %s = %s" % (desc, value))
        if desc == 'Complete Local Name' and value == 'oCare100_MBT':
            addresses.append(dev.addr)

for address in addresses:
    connect(address)
