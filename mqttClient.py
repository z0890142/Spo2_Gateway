import paho.mqtt.client as mqtt
import threading



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
class MqttClient:
    def __init__(self, address ):
        self.address=address
        self.client=mqtt.Client()
        print("broker address : "+address)
    def init(self):
        t = threading.Thread(target = self.connect)
        t.start()
    def connect(self):
        self.client.on_connect= on_connect
        self.client.on_message = on_message
        
        self.client.connect(self.address,1883,600)
        self.client.loop_forever()

    def pushMsg(self,topic,Msg,qos):
        self.client.publish(topic,payload=Msg,qos=qos)


