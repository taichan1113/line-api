from flask import Flask, request, abort

import paho.mqtt.client as mqtt

import os

from linebot import (
   LineBotApi, WebhookHandler
)
from linebot.exceptions import (
   InvalidSignatureError
)
from linebot.models import (
   MessageEvent, TextMessage, TextSendMessage, FollowEvent,
   ImageMessage, AudioMessage, PostbackEvent
)

app = Flask(__name__)
# 環境変数取得 
MY_CHANNEL_ACCESS_TOKEN = os.environ["MY_CHANNEL_ACCESS_TOKEN"]
MY_CHANNEL_SECRET = os.environ["MY_CHANNEL_SECRET"]
MY_LINE_USER_ID = os.environ["MY_LINE_USER_ID"]
MY_BEEBOTTE_TOKEN = os.environ["MY_BEEBOTTE_TOKEN"]
# APIの設定 
line_bot_api = LineBotApi(MY_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(MY_CHANNEL_SECRET)
# MQTT
MQTT_TOPIC = 'home_IoT/watering_system'
client = mqtt.Client()
client.tls_set("mqtt.beebotte.com.pem")
client.username_pw_set("token:{}".format(MY_BEEBOTTE_TOKEN))
client.connect("mqtt.beebotte.com", 8883, 60)

# get test
@app.route("/")
def hello_world():
  return "hello world!"
# Webhook request
@app.route("/callback", methods=['POST'])
def callback():
  signature = request.headers['X-Line-Signature']
  body = request.get_data(as_text=True)
  app.logger.info("Request body: " + body)
  try:
    handler.handle(body, signature)
  except InvalidSignatureError:
    abort(400)
  return 'OK'

# ポストバック
@handler.add(PostbackEvent)
def handle_postback(event):
  userID = event.source.user_id
  data = event.postback.data
  line_bot_api.push_message(userID, TextSendMessage(text=data))

# オウム返し
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  msg = event.message.text.encode('utf-8')
  userID = event.source.user_id
  test_msg = [s.encode('utf-8') for s in ['test', 'テスト']]
  if msg in test_msg:
    line_bot_api.push_message(userID, TextSendMessage(text='publishing...'))
    client.publish(MQTT_TOPIC, userID, 1)
  else:
    line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text=event.message.text))

# 友達追加時
@handler.add(FollowEvent)
def handle_follow(event):
  line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text='友達追加ありがとう'))

def on_connect(client, userdata, flag, rc):
  client.subscribe(MQTT_TOPIC, 1)

def on_message(client, userdata, msg):
  userID = msg.payload.decode('utf-8')
  line_bot_api.push_message(userID, TextSendMessage(text='test message published correctly'))
    
if __name__ == "__main__":
    
  client.on_connect = on_connect
  client.on_message = on_message
  client.loop_start()
  
  port = int(os.getenv("PORT"))
  app.run(host="0.0.0.0", port=port)
