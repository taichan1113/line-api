from crypt import methods
import os

from flask import Flask, flash, request, abort, redirect, url_for, send_from_directory, render_template

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
ALLOWED_EXTENSIONS = set(['mp4', 'wmv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allwed_file(filename):
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
  return "hello world!"

# view uploaded file
@app.route("/upload", methods=["GET"])
def uploaded_file_view():
  return render_template("index.html")

# upload  file
@app.route("/uploads", methods=["GET", "POST"])
def upload_file():
  if request.method == "POST":
    # ファイルがなかった場合の処理
    if 'file' not in request.files:
      flash('ファイルがありません')
      return redirect(request.url)
    # データの取り出し
    file = request.files['file']
    # ファイル名がなかった時の処理
    if not file.filename:
      flash('ファイルがありません')
      return redirect(request.url)
    # ファイルのチェック
    if file and allwed_file(file.filename):
      # 危険な文字を削除（サニタイズ処理）
      # filename = secure_filename(file.filename)
      filename = file.filename
      # ファイルの保存
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      # アップロード後のページに転送
      return redirect(url_for('uploaded_file', filename=filename))
  return '''
  <!doctype html>
  <html>
      <head>
          <meta charset="UTF-8">
          <title>
              ファイルをアップロードして判定しよう
          </title>
      </head>
      <body>
          <h1>
              ファイルをアップロードして判定しよう
          </h1>
          <form method = post enctype = multipart/form-data>
          <p><input type=file name = file>
          <input type = submit value = Upload>
          </form>
      </body>
  '''

@app.route('/uploads/<filename>')
# ファイルを表示する
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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

  port = int(os.getenv("PORT"))
  app.run(host="0.0.0.0", port=port)
