import json 
from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate
from datetime import datetime






# Notification Delegate
class MyDelegate(btle.DefaultDelegate):
    def __init__(self, id,mqttClient,lineNotify):
        DefaultDelegate.__init__(self)
        self.id = id
        self.mqttClient=mqttClient
        self.lineNotify=lineNotify
        self.lineNotify.NotifyMessage("device connect : "+self.id)

    def handleNotification(self, cHandle, data):
        if str(cHandle)=="28":     
            print('cHandle:' + str(cHandle))
            data = ("".join("\\x{:02x}".format(c) for c in data)).split("\\")
            print("Spo2=" + str(int('0' + data[3], 16)))
            print("Bpm= " + str(int('0' + data[5], 16)))
            _payload={"DeviceId":self.id,"Spo2":int('0' + data[3], 16),"Bpm":int('0' + data[5], 16)}
            JsonPayLoad = json.dumps(_payload)
            self.mqttClient.pushMsg('spo2', JsonPayLoad ,0)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)



class BleHandler:
    def __init__(self,  devAddr,mqttClient,lineNotify):
        self.devAddr = devAddr
        self.date_time = datetime.now().strftime("%Y%m%d")
        self.mqttClient=mqttClient
        self.lineNotify=lineNotify
    def BleConnect(self):
        try:
            dev = btle.Peripheral(self.devAddr , "random")
            dev.setDelegate(MyDelegate(self.devAddr+self.date_time,self.mqttClient,self.lineNotify))
            dev.readCharacteristic(17)
            dev.writeCharacteristic(29, b"\x01\x00")
            while True:
                if dev.waitForNotifications(1):
                    continue
                print("Waiting...")
        except btle.BTLEException as e:
            if e.message == "Failed to connect to peripheral "+self.devAddr +", addr type: random":
                self.BleConnect()
            elif e.message == "Device disconnected":
                self.lineNotify.NotifyMessage("device disconnected : "+self.devAddr)
                self.BleConnect()
        


