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
   ImageMessage, AudioMessage,
)

app = Flask(__name__)
# 環境変数取得 
MY_CHANNEL_ACCESS_TOKEN = os.environ["MY_CHANNEL_ACCESS_TOKEN"]
MY_CHANNEL_SECRET = os.environ["MY_CHANNEL_SECRET"]
MY_BEEBOTTE_TOKEN = os.environ["MY_BEEBOTTE_TOKEN"]
# APIの設定 
line_bot_api = LineBotApi(MY_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(MY_CHANNEL_SECRET)
# MQTT
client = mqtt.Client()
client.tls_set("mqtt.beebotte.com.pem")
client.username_pw_set("token:{}".format(MY_BEEBOTTE_TOKEN))

# MQTT publish
def publish_gpio_control_msg(msg):
    client.connect("mqtt.beebotte.com", 8883, 60)
    client.publish("home_IoT/watering_system", msg, 1)

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

# オウム返しプログラム 
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.encode('utf-8')
    led_msg = [s.encode('utf-8') for s in ['LED', '電気']]
    if msg in led_msg:
        publish_gpio_control_msg('on')
    elif msg == 'ID'.encode('utf-8'):
        try:
            id_msg = event.source.user_id
        except:
            id_msg = 'error'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=id_msg))
    else:
        line_bot_api.reply_message(
           event.reply_token,
           TextSendMessage(text=event.message.text))
# 友達追加時イベント 
@handler.add(FollowEvent)
def handle_follow(event):
   line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text='友達追加ありがとう'))


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)