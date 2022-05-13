import os

from flask import Flask, request, abort

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

from Service.waterService import WaterService

app = Flask(__name__)
# ENV. variable 
MY_CHANNEL_ACCESS_TOKEN = os.environ["MY_CHANNEL_ACCESS_TOKEN"]
MY_CHANNEL_SECRET = os.environ["MY_CHANNEL_SECRET"]
MY_LINE_USER_ID = os.environ["MY_LINE_USER_ID"]
MY_BEEBOTTE_TOKEN = os.environ["MY_BEEBOTTE_TOKEN"]
# LINE API settings
line_bot_api = LineBotApi(MY_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(MY_CHANNEL_SECRET)
# MQTT settings
MQTT_TOPIC = 'home_IoT/watering_system'

# Test (GET)
@app.route("/")
def hello_world():
  return "hello world!"

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
  data = event.postback.data
  line_bot_api.push_message(userID, TextSendMessage(text=data))

  if data == 'service=water':
    service = WaterService(MY_BEEBOTTE_TOKEN, MQTT_TOPIC)
    service.serve()
    line_bot_api.push_message(userID, TextSendMessage(text=service.message))

# repeat message bot
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  msg = event.message.text.encode('utf-8')
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
  port = int(os.getenv("PORT"))
  app.run(host="0.0.0.0", port=port)
