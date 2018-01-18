import cv2
import boto3
import numpy as np
import requests
import datetime
import time
import sys
import subprocess

collectionToUse = ''
usernameToUse = ''

if len(sys.argv) == 1:
    print("parameter has to be your email address")
    exit(1)
elif len(sys.argv) == 2:
    argument1 = sys.argv[1]
elif len(sys.argv) == 4:
    argument1 = sys.argv[1]
    collectionToUse = sys.argv[2]
    usernameToUse = sys.argv[3]

url = ''
email = ''
master = 'y'

# check if process is master
if 'http' in argument1:
    url = argument1
    master = 'n'
else:
    email = argument1

username = email.replace('@', '-')
bucket = 'rekon-fbpics'

def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = requests.get(url, auth=('mtryhoen', '!lente11'))
    respbytes = resp.content
    # return the image in bytes
    return respbytes

def get_ipcam():
    ddb = boto3.client('dynamodb')
    try:
        response = ddb.get_item(
            Key={
                'email': {
                    'S': email,
                },
            },
            TableName='users',
        )
        ipcamlist = response['Item']['ipcam']['L']
        print(ipcamlist)
        return ipcamlist
    except:
        return 0


if master == 'y':
    print('master')
    while True:
        ipcamlist = get_ipcam()
        proclist = []
        #  start subprocess here
        for ipcam in ipcamlist:
            print(url)
            url = ipcam['M']['Ipcam']['S']
            collection = ipcam['M']['Collection']['S']
            proc = subprocess.Popen(['python3', 'cv2_ipcam.py', url, collection, username])
            proclist.append(proc)
        # wait before checking DB again
        time.sleep(30)
        for p in proclist:
            p.terminate()
else:
    while True:
        time.sleep(1)
        # get time
        t = datetime.datetime.now()
        today = datetime.date.today()
        filename = str(today) + '-' + str(t.hour) + '-' + str(t.minute) + '-' + str(t.second) + '.jpg'
        bytes = url_to_image(url)
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
                # flags=cv2.CV_HAAR_SCALE_IMAGE
            )

            if type(faces) is tuple:
                print('Y a personne')
            elif faces.size:
                print('Y a qqu')
                s3con = boto3.client('s3')

                response = s3con.put_object(
                    ACL='public-read',
                    Body=bytes,
                    Bucket=bucket,
                    Key=usernameToUse + '/' + filename
                )

                response = s3con.put_object_tagging(
                    Bucket=bucket,
                    Key=usernameToUse + '/' + filename,
                    Tagging={
                        'TagSet': [
                            {
                                'Key': 'collection',
                                'Value': str(collectionToUse)
                            }
                        ]
                    }
                )
