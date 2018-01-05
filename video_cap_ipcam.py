# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at
#     http://aws.amazon.com/asl/
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.

import urllib.request
import sys
import boto3
import cv2
from multiprocessing import Pool
import numpy as np



rekog_client = boto3.client("rekognition")

#Frame capture parameters
default_capture_rate = 30 #frame capture rate.. every X frames. Positive integer.

#Rekognition paramters
rekog_max_labels = 123
rekog_min_conf = 50.0


def main():

    ip_cam_url = ''
    capture_rate = default_capture_rate
    argv_len = len(sys.argv)

    if argv_len > 1:
        ip_cam_url = sys.argv[1]
        
        if argv_len > 2 and sys.argv[2].isdigit():
            capture_rate = int(sys.argv[2])
    else:
        print("usage: video_cap_ipcam.py <ip-cam-url> [capture-rate]")
        return

    print("Capturing from '{}' at a rate of 1 every {} frames...".format(ip_cam_url, capture_rate))
    # create a password manager
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    # Add the username and password.
    # If we knew the realm, we could use it instead of None.
    top_level_url = ip_cam_url
    password_mgr.add_password("Internet Camera", top_level_url, 'admin', '!lente11')

    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib.request.build_opener(handler)

    # use the opener to fetch a URL
    opener.open(ip_cam_url)

    # Install the opener.
    # Now all calls to urllib.request.urlopen use our opener.
    urllib.request.install_opener(opener)

    stream = urllib.request.urlopen(ip_cam_url)

    bytes = ''
    pool = Pool(processes=3)

    frame_count = 0
    while True:
        # Capture frame-by-frame
        frame_jpg = ''

        #bytes += str(stream.read(16384*2))
        bytes = stream
        b = bytes.rfind('\xff\xd9')
        a = bytes.rfind('\xff\xd8', 0, b-1)

        print('a:' + str(a) + 'b:' + str(b))
        if a != -1 and b != -1:
            print ('Found JPEG markers. Start {}, End {}'.format(a,b))
            
            frame_jpg_bytes = bytes[a:b+2]
            bytes = bytes[b+2:]

            if frame_count % capture_rate == 0:
                print ('processing frame')
                #You can perform any image pre-processing here using OpenCV2.
                #Rotating image 90 degrees to the left:
                nparr = np.fromstring(frame_jpg_bytes, dtype=np.uint8)
                
                #Simple and efficient rotation: 90 degrees left = flip + transpose
                #img_cv2_mat = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                #rotated_img = cv2.transpose(cv2.flip(img_cv2_mat, 0))
                gray = cv2.cvtColor(nparr, cv2.COLOR_BGR2GRAY)
                faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
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
                    print('Y a quelqu\'un!')
                
                #Computationally-intensive rotation
                # (h,w) = img_cv2_mat.shape[:2]
                # center = (w/2, h/2)

                # rot_mat = cv2.getRotationMatrix2D(center, -90, 1.0)
                # rotated = cv2.warpAffine(img_cv2_mat, rot_mat, (w, h))
                
                #retval, new_frame_jpg_bytes = cv2.imencode(".jpg", rotated_img)

                #Send to Kinesis
                #result = pool.apply_async(send_jpg, (bytearray(new_frame_jpg_bytes), frame_count, True, False, False,))

            frame_count += 1

if __name__ == '__main__':
    main()
