import os
import json
import requests

# Line Notify
# 「access_token」を環境変数に設定してください。
ACCESS_TOKEN = os.environ["access_token"]
HEADERS = {"Authorization": "Bearer %s" % ACCESS_TOKEN,"Content-Type": "application/json"}
URL = "https://api.line.me/v2/bot/message/broadcast"

def lambda_handler(event, context):

    for record in event['Records']:

        #データ取得
        tm = record['dynamodb']['NewImage']['GetDateTime']['S']
        tm = "{0:s}時{1:s}分{2:s}秒".format(tm[11:13] ,tm[14:16] ,tm[17:19])
        tmp = record['dynamodb']['NewImage']['Temperature']['N']
        hum = record['dynamodb']['NewImage']['Humidity']['N']
        payload = "測定時刻 {0}、気温 {1:.1f}℃、湿度 {2:.1f}%".format(tm ,float(tmp) ,float(hum))

        #送信データ設定
        send_data = {"messages": [{"type":"text","text":payload}]}

        #lineに通知
        r = requests.post(URL, headers=HEADERS, json=send_data)

    return {
        'statusCode': 200,
        'body': 'HTTPStatusFromLineAPI:' + str(r.status_code)
    }
