from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate
import configparser
from datetime import datetime
import base64
import threading
import json 
from mqttClient import MqttClient
from lineMsg import LineClient

# Notification Delegate
class MyDelegate(btle.DefaultDelegate):
    def __init__(self, id):
        DefaultDelegate.__init__(self)
        self.id = id

    def handleNotification(self, cHandle, data):
        print('cHandle:' + str(cHandle))
        data = ("".join("\\x{:02x}".format(c) for c in data)).split("\\")
        print("Spo2=" + str(int('0' + data[3], 16)))
        print("Bpm= " + str(int('0' + data[5], 16)))
        _payload={"DeviceId":self.id,"Spo2":int('0' + data[3], 16),"Bpm":int('0' + data[5], 16)}
        JsonPayLoad = json.dumps(_payload)
        mqttClient.pushMsg('spo2', JsonPayLoad ,0)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)

class ConnectionHandlerThread(threading.Thread):
    def __init__(self, connection_index, devAddr):
        threading.Thread.__init__(self)
        self.connection_index = connection_index
        self.devAddr = devAddr
        lineClient.NotifyMessage("device connect : "+devAddr)

    def run(self):
        
        try:
            connection = connections[self.connection_index]
            connection.setDelegate(MyDelegate(self.devAddr+date_time))

            connection.readCharacteristic(17)
            connection.writeCharacteristic(29, b"\x01\x00")
            while True:
                if connection.waitForNotifications(1):
                    continue
                print("Waiting...")
        except btle.BTLEException as e:
            if e.message == "Device disconnected":
                lineClient.NotifyMessage("device connect : "+self.devAddr)
                reconnect(self.devAddr)



def connect(devAddr):
    try:
        dev = btle.Peripheral(devAddr, "random")

        connections.append(dev)
        t = ConnectionHandlerThread(len(connections) - 1, devAddr)
        t.start()
        connection_threads.append(t)
    except btle.BTLEException as e:
        if e.message == "Failed to connect to peripheral "+devAddr +", addr type: random":
            reconnect(devAddr)

       
def reconnect(devAddr):
    print("reconnecting...")
    connect(devAddr)


date_time = datetime.now().strftime("%Y%m%d")
config = configparser.ConfigParser()
config.read('./config/config.ini')
broker = config.get('default', 'broker')
token = config.get('default', 'AesToken')
lineClient=LineClient(token)
lineClient.NotifyMessage("spo2 gateway start!!")
lineClient.NotifyMessage("mqtt broker address : "+broker)

connections = []
connection_threads = []

mqttClient=MqttClient(broker)
mqttClient.init()

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
