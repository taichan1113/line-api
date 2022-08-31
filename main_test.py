from crypt import methods
import os

from flask import Flask, flash, request, abort, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

from linebot import (
   LineBotApi, WebhookHandler
) 
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
   MessageEvent, TextMessage, TextSendMessage, FollowEvent,
   ImageMessage, AudioMessage, PostbackEvent
)

import paho.mqtt.client as mqtt


UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = set(['mp4', 'wmv', 'jpg', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ENV. variable 
MY_CHANNEL_ACCESS_TOKEN = os.environ["MY_CHANNEL_ACCESS_TOKEN"]
MY_CHANNEL_SECRET = os.environ["MY_CHANNEL_SECRET"]
MY_LINE_USER_ID = os.environ["MY_LINE_USER_ID"]
MY_BEEBOTTE_TOKEN = os.environ["MY_BEEBOTTE_TOKEN"]
# LINE API settings
line_bot_api = LineBotApi(MY_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(MY_CHANNEL_SECRET)
# MQTT settings
MQTT_TOPIC_SERVER = 'home_IoT/watering_system_server'
MQTT_TOPIC_DEVICE = 'home_IoT/watering_system_device'
client = mqtt.Client()
client.tls_set("mqtt.beebotte.com.pem")
client.username_pw_set("token:{}".format(MY_BEEBOTTE_TOKEN))
client.connect("mqtt.beebotte.com", 8883, 60)
def onConnect(client, userdata, flag, rc):
  client.subscribe(MQTT_TOPIC_SERVER, 1)
def onMessage(client, userdata, msg):
  message = msg.payload.decode('utf-8')
  line_bot_api.push_message(MY_LINE_USER_ID, TextSendMessage(text=message))

# Test (GET)
@app.route("/")
def hello_world():
  return "Hello from PONTA!"

# Webhook request (POST)
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

# postback
@handler.add(PostbackEvent)
def handle_postback(event):
  userID = event.source.user_id
  if userID != MY_LINE_USER_ID:
    return
  data = event.postback.data
  # line_bot_api.push_message(userID, TextSendMessage(text=data))
  client.publish(MQTT_TOPIC_DEVICE, data, 1)
  client.publish(MQTT_TOPIC_SERVER, data, 1)

# repeat message bot
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  print('get message')
  msg = event.message.text
  line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=msg))

# follow event
@handler.add(FollowEvent)
def handle_follow(event):
  line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text='友達追加ありがとう'))

if __name__ == "__main__":
  client.on_connect = onConnect
  client.on_message = onMessage
  client.loop_start()

  # port = int(os.getenv("PORT"))
  app.run(host="0.0.0.0", port=80, debug=True)
