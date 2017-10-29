import cv2
import sys
import boto3
# import msvcrt
import polly

ACCOUNT = 'default'#'perso'
region = 'eu-west-1'
client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')

SIMILARITY_THRESHOLD = 70.0
COLLECTION = 'famille'

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
        '''
        glasses=faceinfo[0]['Eyeglasses']['Value']
        for emotion in faceinfo[0]['Emotions']:
            if emotion['Confidence'] > 50:
                goodemotion=emotion['Type']
                break
            else:
                goodemotion="Pas d'emotion"

        if glasses:
            glasses="lunettes"
        else:
            glasses="pas de lunettes"
        '''

        if gender == "Male":
            gender="Monsieur"
        else:
            gender="Madame"


        #if glasses == "True":
        #    glasses="Venez profiter de nos promotions sur les lunettes"
        #else:
        #    glasses="Pas de lunettes"

        # return ("Bonjour " + gender + ", " + glasses + ", " + goodemotion)
        return (gender)

    except:
        return "Problem"

def rekon(COLLECTION, target_bytes):
    try:
        collection_match = client.search_faces_by_image(
            CollectionId= COLLECTION,
            Image={
                'Bytes': target_bytes
            },
            FaceMatchThreshold=SIMILARITY_THRESHOLD
        ).get('FaceMatches', [])
    except:
        return("Pas reconnu.")

    try:
        if collection_match[0]['Similarity'] > 75:
            ImageId = collection_match[0]['Face']['ExternalImageId']
            return (ImageId)
        else:
            return("Pas reconnu...")
    except:
        return('Pas reconnu !')

imageid=0
while True:
    # if msvcrt.kbhit():
    #     if ord(msvcrt.getch()) == 32:
    #         break
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
        #with open('C:\\Users\\mtryhoen\\Pictures\\famille\\alice.jpg', 'rb') as target_image:
            target_bytes = target_image.read()
        #target_bytes = frame.tobytes()

        id=rekon(COLLECTION, target_bytes)
        if imageid == id:
            print("Deja vu!")
            continue
        elif "Pas reconnu" in id:
            continue
        else:
            imageid=id
            print(id)

        gender=getinfo(target_bytes)
        text="Bonjour " + gender + ". Vous vous appelez " + imageid + ". N'est-ce pas?"
        if id == "nico":
            text=text + " Est-ce que la collection SALLSKAP vous plait?"
        polly.talk(text)
        #print(gender)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
