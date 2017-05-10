import cv2
import sys
import boto3
import numpy as np

ACCOUNT = 'perso'
region = 'eu-west-1'
client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')

SIMILARITY_THRESHOLD = 20.0

cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)

#Number of frames to throw away while the camera adjusts to light levels
ramp_frames = 5
file = "C:\\Users\\mtryhoen\\Pictures\\test_image.png"

def getinfo(target_bytes):
    try:
        faceinfo = client.detect_faces(
            Image={
                'Bytes': target_bytes,
            },
            Attributes=[
                'ALL',
            ]
        ).get('FaceDetails', [])
        gender=faceinfo[0]['Gender']['Value']
        glasses=faceinfo[0]['Eyeglasses']['Value']
        for emotion in faceinfo[0]['Emotions']:
            print(str(emotion))
            if emotion['Confidence'] > 80:
                goodemotion=emotion['Type']
                print(goodemotion)
            else:
                print(str(emotion['Confidence']))

        if glasses:
            glasses="lunettes"
        else:
            glasses="pas de lunettes"

        print(gender + ", " +glasses + ", " + goodemotion)

        if gender == "Male":
            gender="Monsieur"
        else:
            gender="Madame"


        #if glasses == "True":
        #    glasses="Venez profiter de nos promotions sur les lunettes"
        #else:
        #    glasses="Pas de lunettes"

        return ("Bonjour " + gender)

    except:
        return "Problem"

def rekon(target_bytes):
    try:
        collection_match = client.search_faces_by_image(
            CollectionId='facedb',
            Image={
                'Bytes': target_bytes
            },
            FaceMatchThreshold=SIMILARITY_THRESHOLD
        ).get('FaceMatches', [])
    except:
        return("Y a personne")

    try:
        if collection_match[0]['Similarity'] > 75:
            ImageId = collection_match[0]['Face']['ExternalImageId']
            return("Salut " + ImageId + " !")
        else:
            return("Pas reconnu...")
    except:
        return('Pas reconnu !')

while True:
    for i in range(ramp_frames):
        rettmp, frametmp = video_capture.read()
    # Capture frame-by-frame
    ret, frame = video_capture.read()


    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
        #flags=cv2.CV_HAAR_SCALE_IMAGE
    )

    if type(faces) is tuple:
        print('Y a personne')
    elif faces.size:
        cv2.imwrite(file, frame)

        with open('C:\\Users\\mtryhoen\\Pictures\\test_image.png', 'rb') as target_image:
            target_bytes = target_image.read()
        #target_bytes = frame.tobytes()

        #name=rekon(target_bytes)
        #print(name)

        gender=getinfo(target_bytes)
        print(gender)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()