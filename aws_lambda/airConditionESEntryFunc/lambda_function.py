import requests
import json
import os

# ElasticSearch Entry
HEADERS = {"Content-Type": "application/json"}
URL = "http://" + os.environ["es_host"] + ":" + os.environ["es_port"]

def lambda_handler(event, context):
    # TODO implement
    for record in event['Records']:
        #データ取得
        tm = record['dynamodb']['NewImage']['GetDateTime']['S']
        tmp = record['dynamodb']['NewImage']['Temperature']['N']
        hum = record['dynamodb']['NewImage']['Humidity']['N']
        data={"GetDateTime":tm,"Humidity":float(hum),"Temperature":float(tmp)}

        #ElasticSearchへ投入
        r = requests.post(URL + "/" + os.environ["index"] + "/_doc" , headers=HEADERS, json=data)
        print(r.text)
    return {
        'statusCode': r.status_code,
        'body': r.text
    }

#Local Execute
#testdata = {"Records":[{"dynamodb":{"NewImage":{"GetDateTime":{"S":"2021-11-03 16:20:18"},"Temperature":{"N":"20.5"},"Humidity":{"N":"72.3"}}}}]}
#lambda_handler(testdata,"")