import paho.mqtt.client as mqtt

class Service:
  def __init__(self, beebotteToken, mqttTopic):
    self.mqttTopic = mqttTopic
    self.beebotteToken = beebotteToken

    client = mqtt.Client()
    client.tls_set("mqtt.beebotte.com.pem")
    client.username_pw_set("token:{}".format(self.beebotteToken))
    client.connect("mqtt.beebotte.com", 8883, 60)

    client.on_connect = self.onConnect
    client.on_message = self.onMessage
    client.loop_start()

  # MQTT methods
  def onConnect(self, client, userdata, flag, rc):
    client.subscribe(self.mqttTopic, 1)

  def onMessage(self, client, userdata, msg):
    message = msg.payload.decode('utf-8')
    # line_bot_api.push_message(MY_LINE_USER_ID, TextSendMessage(text=message))
