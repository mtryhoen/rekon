import boto3
import json
import urllib.request as urllib2
import urllib.parse as urllib
import io
import requests
import unicodedata
import dynamo
import savepic

GROUP = 'lecoursiermontois7000mons'

ACCOUNT = 'perso'
region = 'eu-west-1'

dyn=boto3.client('dynamodb')
tables = dyn.list_tables().get('TableNames',[])
if 's3pic' not in tables:
    tablename=dynamo.create()
    print(tablename)

client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')
collections = client.list_collections().get('CollectionIds',[])
if 'facedb' not in collections:
    print("Creating Collection facedb")
    response = client.create_collection(
        CollectionId='facedb'
    )
else:
    '''
    with open('C:\\Users\\mtryhoen\\Pictures\\test_image_init.png', 'rb') as source_image:
        source_bytes = source_image.read()
        response = client.index_faces(
            CollectionId='facedb',
            Image={
                'Bytes': source_bytes
            },
            ExternalImageId='Max'
        )
    exit(0)
    '''
    print("Collection facedb already exists, cleaning")
    response = client.delete_collection(
        CollectionId='facedb'
    )
    response = client.create_collection(
        CollectionId='facedb'
    )
    #exit(1)

#Number of frames to throw away while the camera adjusts to light levels

file = "C:\\Users\\mtryhoen\\Pictures\\test_image.png"

ACCESS_TOKEN = 'EAACEdEose0cBAEukkbxajOjEkciNJNLpCC7H93y4gbv5Ij1RcWE5InO0wNF3ZBM2B75LXUgzaSVZClYZBEFlMn1Mb1ZBEaYuarU3zBFIuiFUmbqXihArX0TW001YrtqQMuZC2sGVvD0mFEqViZCkdrKs5GmQQRTi1l2exltddjYCMyce9TGfVjtYEhlLAl0x8ZD'
#exit(0)

# build the URL for the API endpoint
host = "https://graph.facebook.com"

#get group id
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

#Get group members
path = "/" + GROUPID + "/members"
params = urllib.urlencode({"access_token": ACCESS_TOKEN})
url = "{host}{path}?{params}".format(host=host, path=path, params=params)
MEMID = {}

# open the URL and read the response
resp = urllib2.urlopen(url).read().decode('utf-8')
# convert the returned JSON string to a Python datatype
members = json.loads(resp)
for member in members['data']:
    MEMID[member['id']]=member['name']

url = members['paging']['next']
while(url):
    resp = urllib2.urlopen(url).read().decode('utf-8')
    members = json.loads(resp)
    for member in members['data']:
        MEMID[member['id']] = member['name']

    try:
        url = members['paging']['next']
    except:
        url = ""

#Get profile pictures
for memberid, membername in MEMID.items():
    #member = '10154479345032683'
    membername=membername.split()[0]
    try:
        memberlastname=membername.split()[1]
    except:
        memberlastname=''
    membername=unicodedata.normalize('NFKD', membername).encode('ASCII', 'ignore').decode('UTF-8')
    memberlastname = unicodedata.normalize('NFKD', memberlastname).encode('ASCII', 'ignore').decode('UTF-8')
    if len(membername) < 1:
        membername='inconnu'

    print (memberid + '-' + membername + '-' + memberlastname)
    path = "/" + memberid + "/picture"
    params = urllib.urlencode({"type": "large", "access_token": ACCESS_TOKEN})
    url = "{host}{path}?{params}".format(host=host, path=path, params=params)
    # Our target image: http://i.imgur.com/Xchqm1r.jpg
    with urllib2.urlopen(url) as url:
        target_bytes = io.BytesIO(url.read()).read()

    confidence = 0
    try:
        response = client.detect_faces(
            Image={
                'Bytes': target_bytes
            }
        ).get('FaceDetails',[])
        #print(response)
        confidence = response[0]['Confidence']

        print("Confidence for " + memberid + " is " + str(confidence) )

    except:
        print("No face detected")

    if confidence > 75:
        savepic.dynsave(memberid, membername, memberlastname, target_bytes)
        response = client.index_faces(
            CollectionId='facedb',
            Image={
                'Bytes': target_bytes
            },
            ExternalImageId=membername
        )
