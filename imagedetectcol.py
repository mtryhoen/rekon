import cv2
import sys
import boto3

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
        #print (faces)
        #input("Press Enter to continue...")
        with open('C:\\Users\\mtryhoen\\Pictures\\test_image.png', 'rb') as target_image:
        #with open('C:\\Users\\mtryhoen\\Pictures\\marie.jpg', 'rb') as target_image:
            target_bytes = target_image.read()
        try:
            collection_match = client.search_faces_by_image(
                CollectionId='facedb',
                Image={
                    'Bytes': target_bytes
                },
                FaceMatchThreshold=SIMILARITY_THRESHOLD
            ).get('FaceMatches',[])
        except:
            print ("Y a personne")

        #print(type(collection_match[0]))

        try:
            if collection_match[0]['Similarity'] > 75:
                ImageId = collection_match[0]['Face']['ExternalImageId']
                print("Salut " + ImageId + " !")
            else:
                print("Pas reconnu...")
        except:
            print('Pas reconnu !')
    '''
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    '''

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()