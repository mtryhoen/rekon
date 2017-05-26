import boto3
import json
import urllib.request as urllib2
import urllib.parse as urllib
import io
import unicodedata
import os
import cv2
import sys

#GROUP = 'lecoursiermontois7000mons'
GROUP = 'Fleurs a Couper'
#GROUP = 'Ducati DESMO Fans !!!!!'
COLLECTION = 'famille'
#COLLECTION = 'facedb'
DIR = 'C:\\Users\\mtryhoen\\Pictures\\famille'
file = "C:/Users/mtryhoen/Pictures/test_image.png"
cascPath = sys.argv[1]
ACCOUNT = 'perso'
region = 'eu-west-1'
bucket="rekon-fbpics"
ACCESS_TOKEN = 'EAACEdEose0cBAHCCXVLT5TAa6gKYsv9TuDMZBiZAWXT9WiRvKZCi7YZAZCmoAhMpkRSD4z4t64Vla9ZANWHibxhYZCn7f0ZCOMlIxS8QsziqzM98ZBoDxBAtEpBCRoFlEbIyQfkocHr3n3acdcgsUU4hE58tOR0KRE8gCahYVw5egRebjoqVyZAFHp'


def createFromDir(COLLECTION, DIR):
    client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')
    collections = client.list_collections().get('CollectionIds', [])
    if COLLECTION not in collections:
        print("Creating Collection " + COLLECTION)
        response = client.create_collection(
            CollectionId=COLLECTION
        )
    else:
        print("Collection " + COLLECTION + " already exists, cleaning")
        response = client.delete_collection(
            CollectionId=COLLECTION
        )
        response = client.create_collection(
            CollectionId=COLLECTION
        )

    for root, dirs, filenames in os.walk(DIR):
        for f in filenames:
            with open(os.path.join(root, f), 'rb') as source_image:
                source_bytes = source_image.read()
                response = client.index_faces(
                    CollectionId=COLLECTION,
                    Image={
                        'Bytes': source_bytes
                    },
                    ExternalImageId=f.split(".")[0]
                )


def createFromFB():
    client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')
    # build the URL for the API endpoint
    host = "https://graph.facebook.com"

    # get group id
    path = "/search"
    params = urllib.urlencode({"q": GROUP, "type": "group", "access_token": ACCESS_TOKEN})
    url = "{host}{path}?{params}".format(host=host, path=path, params=params)

    print(url)
    # open the URL and read the response
    resp = urllib2.urlopen(url).read().decode('utf-8')
    # convert the returned JSON string to a Python datatype
    id = json.loads(resp)
    GROUPID = id['data'][0]['id']
    print (GROUPID)

    # Get group members
    path = "/" + GROUPID + "/members"
    params = urllib.urlencode({"access_token": ACCESS_TOKEN})
    url = "{host}{path}?{params}".format(host=host, path=path, params=params)
    MEMID = {}

    # open the URL and read the response
    resp = urllib2.urlopen(url).read().decode('utf-8')
    # convert the returned JSON string to a Python datatype
    members = json.loads(resp)
    for member in members['data']:
        MEMID[member['id']] = member['name']

    url = members['paging']['next']
    while (url):
        resp = urllib2.urlopen(url).read().decode('utf-8')
        members = json.loads(resp)
        for member in members['data']:
            MEMID[member['id']] = member['name']
        try:
            url = members['paging']['next']
        except:
            url = ""

    print(len(MEMID))
    exit(0)
    # Get profile pictures
    for memberid, membername in MEMID.items():
        membername = membername.split()[0]
        membername = unicodedata.normalize('NFKD', membername).encode('ASCII', 'ignore').decode('UTF-8')
        if len(membername) < 1:
            membername = 'inconnu'
        print (membername)
        path = "/" + memberid + "/picture"
        params = urllib.urlencode({"type": "large", "access_token": ACCESS_TOKEN})
        url = "{host}{path}?{params}".format(host=host, path=path, params=params)
        print(memberid + '-' + membername)
        with urllib2.urlopen(url) as url:
            target_bytes = io.BytesIO(url.read()).read()

        confidence = 0
        try:
            response = client.detect_faces(
                Image={
                    # 'Bytes': target_bytes
                    'S3Object': {
                        'Bucket': 'mybucket',
                        'Name': 'myphoto',
                    }
                }
            ).get('FaceDetails', [])
            confidence = response[0]['Confidence']
            print("Confidence for " + memberid + " is " + str(confidence))
        except:
            print("No face detected")

        if confidence > 75:
            response = client.index_faces(
                CollectionId=COLLECTION,
                Image={
                    'Bytes': target_bytes
                },
                ExternalImageId=membername
            )


def createFromS3(COLLECTION, ACCOUNT, region, bucket):
    client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('s3')

    #with open('C:\\Users\\mtryhoen\\Pictures\\test_image.png', 'rb') as target_image:
    #    target_bytes = target_image.read()

    rekon = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')
    collections = rekon.list_collections().get('CollectionIds', [])
    if COLLECTION not in collections:
        print("Creating Collection " + COLLECTION)
        response = rekon.create_collection(
            CollectionId=COLLECTION
        )
    else:
        print("Collection " + COLLECTION + " already exists, cleaning")
        response = rekon.delete_collection(
            CollectionId=COLLECTION
        )
        response = rekon.create_collection(
            CollectionId=COLLECTION
        )

    istrunk=1
    marker=''
    while istrunk:
        objects = client.list_objects(Bucket=bucket, Marker=marker)
        photos = objects.get('Contents')
        marker = objects.get('NextMarker')

        for photo in photos:
            imgname = photo['Key'].split("/")[1].split("_")[1].replace("-", "")
            imgkey = photo['Key']
            response = rekon.index_faces(
                CollectionId=COLLECTION,
                Image={
                    #'Bytes': target_bytes
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': imgkey
                    }
                },
                ExternalImageId=imgname
            )
        istrunk = objects.get('IsTruncated')


def Fb2S3(GROUP, ACCESS_TOKEN, file, cascPath, bucket):

    faceCascade = cv2.CascadeClassifier(cascPath)
    s3 = boto3.Session(profile_name=ACCOUNT, region_name=region).client('s3')
    # build the URL for the API endpoint
    host = "https://graph.facebook.com"

    # get group id
    path = "/search"
    params = urllib.urlencode({"q": GROUP, "type": "group", "access_token": ACCESS_TOKEN})
    url = "{host}{path}?{params}".format(host=host, path=path, params=params)

    print(url)
    # open the URL and read the response
    resp = urllib2.urlopen(url).read().decode('utf-8')
    # convert the returned JSON string to a Python datatype
    id = json.loads(resp)
    GROUPID = id['data'][0]['id']
    print (GROUPID)

    # Get group members
    path = "/" + GROUPID + "/members"
    params = urllib.urlencode({"access_token": ACCESS_TOKEN})
    url = "{host}{path}?{params}".format(host=host, path=path, params=params)
    MEMID = {}

    # open the URL and read the response
    resp = urllib2.urlopen(url).read().decode('utf-8')
    # convert the returned JSON string to a Python datatype
    members = json.loads(resp)
    for member in members['data']:
        MEMID[member['id']] = member['name']

    url = members['paging']['next']
    while (url):
        resp = urllib2.urlopen(url).read().decode('utf-8')
        members = json.loads(resp)
        for member in members['data']:
            MEMID[member['id']] = member['name']
        try:
            url = members['paging']['next']
        except:
            url = ""

    print(str(len(MEMID)) + "members in the group")

    # Get profile pictures
    for memberid, membername in MEMID.items():
        membername = membername.split()[0]
        membername = unicodedata.normalize('NFKD', membername).encode('ASCII', 'ignore').decode('UTF-8')
        if len(membername) < 1:
            continue
        path = "/" + memberid + "/picture"
        params = urllib.urlencode({"type": "large", "access_token": ACCESS_TOKEN})
        url = "{host}{path}?{params}".format(host=host, path=path, params=params)
        print(memberid + '-' + membername)
        with urllib2.urlopen(url) as url:
            target_bytes = io.BytesIO(url.read()).read()

        with open(file, "wb") as f:
            f.write(target_bytes)

        img = cv2.imread(file)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
            # flags=cv2.CV_HAAR_SCALE_IMAGE
        )

        if type(faces) is tuple:
            continue
        elif faces.size:
            print('Saving to S3...')
            s3.put_object(
                Body=target_bytes,
                Bucket=bucket,
                Key=(memberid + "_" + membername.lower() + "/1.jpg"),
                #Key=memberid,
                StorageClass='REDUCED_REDUNDANCY',
                Metadata={
                    'Content-Type':'image/jpeg'
                }
            )


#Fb2S3(GROUP, ACCESS_TOKEN, file, cascPath, bucket)
#createFromS3(COLLECTION, ACCOUNT, region, bucket)
#createFromFB()
createFromDir(COLLECTION, DIR)
