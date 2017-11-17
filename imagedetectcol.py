import cv2
import boto3
import msvcrt
import webbrowser
import os
import polly
from tkinter import *
from PIL import ImageTk, Image

ACCOUNT = 'perso'
region = 'eu-west-1'
SIMILARITY_THRESHOLD = 60.0
COLLECTION = 'famille'
cascPath = sys.argv[1]

############################# Face attributes detection #####################################3
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

##################### Face rekognition ####################################33

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

################################# DISPLAY IMAGE #########################################33

def displayimage(pic):
    root = Tk()

    my_image = Image.open(pic)
    filename = ImageTk.PhotoImage(my_image)

    w = Label(root, image = filename)

    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.focus_set()  # <-- move focus to this widget
    root.bind("<Escape>", lambda e: root.quit())
    w.pack(side="bottom", fill="both", expand="yes")
    w.after(10000, lambda: root.destroy())
    root.mainloop()


################################## MAIN LOOP ################################################

faceCascade = cv2.CascadeClassifier(cascPath)
video_capture = cv2.VideoCapture(0)
#Number of frames to throw away while the camera adjusts to light levels
ramp_frames = 5
file = "C:\\Users\\mtryhoen\\Pictures\\test_image.png"

client = boto3.Session(profile_name=ACCOUNT, region_name=region).client('rekognition')
imageid=0
while True:
    if msvcrt.kbhit():
        if ord(msvcrt.getch()) == 32:
            break
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

        with open(file, 'rb') as target_image:
        #with open('C:\\Users\\mtryhoen\\Pictures\\famille\\alice.jpg', 'rb') as target_image:
            target_bytes = target_image.read()
        #target_bytes = frame.tobytes()

        id=rekon(COLLECTION, target_bytes)
        if imageid == id:
            print("Deja vu!")
            continue
        elif "Pas reconnu" in id:
            print("Pas reconnu")
            webbrowser.open('file://' + os.path.realpath('index.html'))
            polly.talk("Entrez votre nom. Si je vous reconnais ailleurs dans le magasin, vous recevrez un bon d'achat.")
            continue
        else:
            imageid=id
            print(id)

        gender=getinfo(target_bytes)
        text="Bonjour " + gender + ". Tu t'appelles " + imageid + ". Je te reconnais"
        if id == "nico":
            text=text + " Est-ce que la collection SALLSKAP vous plait?"
        if id == "marie":
            text=text + " Tu es tres belle aujourdh'hui. J'ai envie de te croquer!"
        if id == "antoine":
            text=text + " Est-ce que tu veux que je te mette une racloche a Pokemon?"
        if id == "maxime":
            text = text + " Tu es vraiment le plus fort!"
        if id == "gaspard":
            text = text + " j'espère que tu es gentil avec ton frère Lucien"
        if id == "alice":
            text = text + " Tu es une gentille petit crotte, mais tu dois jeter ta tututte a la poubelle. Sinon, je te mets une mandale. Je sais que ta copine Eva ne prends plus la tututte."
        polly.talk(text)
        displayimage(file)

        #print(gender)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()