from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate
import time
import base64
import threading
import paho.mqtt.client as mqtt
import json 

# print ("Services...")
# services=dev.getServiceByUUID("00001822-0000-1000-8000-00805f9b34fb")
# chs=services.getCharacteristics();
# handle=chs[0].getHandle()
# print(chs[1].valHandle)

# print('test= '+str(handle))

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))

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

        client.publish('spo2', payload=JsonPayLoad ,qos=0)

        # print ('handleNotification:' +"\\x{:02x}".format(str(data)))
        # ... perhaps check cHandle
        # ... process 'data'

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)


connections = []
connection_threads = []


class ConnectionHandlerThread(threading.Thread):
    def __init__(self, connection_index, devAddr):
        threading.Thread.__init__(self)
        self.connection_index = connection_index
        self.devAddr = devAddr

    def run(self):
        
        try:
            connection = connections[self.connection_index]
            connection.setDelegate(MyDelegate(self.devAddr))

            connection.readCharacteristic(17)
            connection.writeCharacteristic(29, b"\x01\x00")
            while True:
                if connection.waitForNotifications(1):
                    continue
                print("Waiting...")
        except btle.BTLEException as e:
            if e.message == "Device disconnected":
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

# def getMsg(dev):
#     while True:
#         if dev.waitForNotifications(1.0):
#             continue
#         print("Waiting...")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883, 600)
# while True:
#     try:
#         scanner =Scanner(0)

#         devices=scanner.scan(10.0)
#         print("scaning")
#         addresses=[]
#         for dev in devices:
#             print ("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
#             for (adtype, desc, value) in dev.getScanData():
#                     # print ("  %s = %s" % (desc, value))
#                 if desc == 'Complete Local Name' and value == 'oCare100_MBT':
#                     addresses.append(dev.addr)

#         for address in addresses:
#             connect(address)
#         time.sleep(3.0)
#     except btle.BTLEException as e:
#         print(e.message)

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
