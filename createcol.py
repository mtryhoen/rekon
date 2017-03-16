import boto3
import json
import urllib.request as urllib2
import urllib.parse as urllib
import io
import requests
import unicodedata

GROUP = 'lecoursiermontois7000mons'

ACCOUNT = 'perso'
region = 'eu-west-1'
client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')


collections = client.list_collections().get('CollectionIds',[])
if 'facedb' not in collections:
    print("Creating Collection facedb")
    response = client.create_collection(
        CollectionId='facedb'
    )
else:
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
    '''

#Number of frames to throw away while the camera adjusts to light levels

file = "C:\\Users\\mtryhoen\\Pictures\\test_image.png"

#########Facebook Graph
FACEBOOK_APP_ID     = '1217401738373219'
FACEBOOK_APP_SECRET = '0d9c39848700d901fac2022031373d0f'



def get_fb_token(app_id, app_secret):
    payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
    file = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
    #print file.text #to test what the FB api responded with
    result = file.text.split("=")[1]
    #print file.text #to test the TOKEN
    return result
# get Facebook access token from environment variable
ACCESS_TOKEN = get_fb_token(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
print(ACCESS_TOKEN)

ACCESS_TOKEN = 'EAACEdEose0cBAAEocT1MSgaMtIAhLRnrKXhQe5eZAkBigrGlNnzvOuTnyyCBFCM4go2HZAZBhBMdX4s7Ij5f87PBBw6rsUl85ZBvNSqKjb84sP0r3EGflY6inGbxTCTsZBu7yMhlcdoT2l3AkA7siBqmkejNY8PByYrISZAZBwFX18UH0Nx9a56GeMZATlcrRWgZD'
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
        if "Fadeur" in member['name']:
            print ("Marie: " + member['id'])
            #exit(0)
    try:
        url = members['paging']['next']
    except:
        url = ""
#print(MEMID)
print(len(MEMID))

#Get profile pictures
for memberid, membername in MEMID.items():
    #member = '10154479345032683'
    membername=membername.split()[0]
    membername=unicodedata.normalize('NFKD', membername).encode('ASCII', 'ignore').decode('UTF-8')
    if len(membername) < 1:
        membername='inconnu'
    print (membername)
    path = "/" + memberid + "/picture"
    params = urllib.urlencode({"type": "large", "access_token": ACCESS_TOKEN})
    url = "{host}{path}?{params}".format(host=host, path=path, params=params)
    print(memberid + '-' + membername)
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

        #if member == "10154479345032683":
        print("Confidence for " + memberid + " is " + str(confidence) )
        #print(len(response))
        #break

    except:
        print("No face detected")
        '''
        if member == "10154479345032683":
            print("Confidence for Marie " + member + " is " + str(confidence))
            print(len(response))
            break
        '''
    if confidence > 75:
        response = client.index_faces(
            CollectionId='facedb',
            Image={
                'Bytes': target_bytes
            },
            ExternalImageId=membername
        )

#params = urllib.urlencode({"access_token": ACCESS_TOKEN})
#url = "{host}{path}?{params}".format(host=host, path=path, params=params)



# display the result
#pprint.pprint(me)

#response = client.delete_collection(
#    CollectionId='facedb'
#)
collections = client.list_collections().get('CollectionIds',[])
if 'facedb' not in collections:
    print("Creating Collection facedb")
    response = client.create_collection(
        CollectionId='facedb'
    )
else:
    print("Collection facedb already exists")
    exit(1)

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
with open('C:\\Users\\mtryhoen\\Pictures\\darts.png', 'rb') as source_image:
    source_bytes = source_image.read()
    response = client.index_faces(
        CollectionId='facedb',
        Image={
            'Bytes': source_bytes
        },
        ExternalImageId='Darts'
    )
with open('C:\\Users\\mtryhoen\\Pictures\\marie.jpg', 'rb') as source_image:
    source_bytes = source_image.read()
    response = client.index_faces(
        CollectionId='facedb',
        Image={
            'Bytes': source_bytes
        },
        ExternalImageId='Marie'
    )
'''