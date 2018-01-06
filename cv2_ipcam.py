import cv2
import boto3
import numpy as np
import requests
import datetime
import time
import sys

url = sys.argv[2]  # 'http://facerekon.ddns.net:5001/camvideo.jpg'
username = sys.argv[1]
username = username.replace('@', '-')
bucket='rekon-fbpics'

def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = requests.get(url, auth=('mtryhoen', '!lente11'))
    respbytes = resp.content
    # return the image in bytes
    return respbytes


while True:
    time.sleep(1)
    # get time
    t = datetime.datetime.now()
    today = datetime.date.today()
    filename = str(today) + '-' + str(t.hour) + '-' + str(t.minute) + '-' + str(t.second) + '.jpg'
    #bytes += stream.read(1024)
    bytes = url_to_image(url)
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        #bytes = bytes[b+2:]
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
                Key=username + '/' + filename
            )
