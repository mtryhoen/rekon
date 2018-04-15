import boto3
import sys
import time
import RPi.GPIO as GPIO

if len(sys.argv) == 1:
    print("parameter has to be your email address")
    exit(1)
elif len(sys.argv) == 2:
    email = sys.argv[1]

ddb = boto3.client('dynamodb')

while True:
    time.sleep(1)
    response = ddb.get_item(
        Key={
            'email': {
                'S': email,
            },
        },
        TableName='users',
    )

    ipcamlist = response['Item']['ipcam']['L']

    for ipcam in ipcamlist:
        if ipcam['M']['Detection']['S'] != 'false':
            collectionName = ipcam['M']['Collection']['S']
            ipcamName = ipcam['M']['Ipcam']['S']
            print("access granted")
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(18, GPIO.OUT)
            GPIO.output(18, GPIO.LOW)
            time.sleep(10)
            GPIO.output(18, GPIO.HIGH)
            GPIO.cleanup()

            response = ddb.update_item(
                UpdateExpression="SET ipcam = :cam",
                ExpressionAttributeValues={
                    ':cam': {
                        "L": [
                            {"M": {"Ipcam": {"S": ipcamName}, "Collection": {"S": collectionName},
                                   "Detection": {"S": 'false'}}}
                        ]
                    }
                },
                Key={
                    'email': {
                        'S': email,
                    },
                },
                TableName='users',
            )
        else:
            print("access closed")


