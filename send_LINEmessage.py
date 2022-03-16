import requests
url = "https://notify-api.line.me/api/notify" 
token = "tYjavU1eyvPoqVh66WTFIIiFZ2Fo83NhzNq6rX7JQ7o"
headers = {"Authorization" : "Bearer "+ token} 
message =  "サンシュユからメッセージ" 
payload = {"message" :  message} 
r = requests.post(url, headers = headers, params=payload) 