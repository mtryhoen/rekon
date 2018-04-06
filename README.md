# rekon

On Ubuntu 17.10,
Install
 - sudo apt-get install python3-pip
 - pip3 install boto3
 - sudo apt-get install python3-dev
 - sudo apt-get install git
 - sudo apt-get install python3-opencv
 - sudo apt install awscli
 - aws configure
 - pip install flask, WTForms

 Clone the repo:
  - git clone https://github.com/mtryhoen/rekon
  
  
# Webapp

docker login \
docker pull mtryhoen/rekon:v0 \
docker run -d -p 5000:5000 rekon:vo 

# rekon app

A client running on docker using cv2 checks regularly the snapshot of defined ip cam to check if there are faces in it;
if yes, the snapshot is copied to S3.
A lambda function compares the face with the defined collection and if there is a match, an email is sent and the corresponding IP cam is highlighted in the app.
The app itself is a flask app deployed using aws beanstalk.

# lambda

To zip the function:
Install required modules in same dir as python script:
pip3 install pillow -t .
cd in the directory where all modules are installed
then
zip -r9 rekon_lambda.zip rekon_lambda.py PIL <other module dir>

# docker client

# build image with Dockerfile
sudo docker build -t "cv2_ipcam:v0.1" .

# create docker network
sudo docker network create --subnet=192.168.0.32/30 dockernet

# start container using docker network
sudo docker run -d --net dockernet --ip 192.168.0.34 cv2_ipcam:v0.1

#connect to container
sudo docker exec -it 0b99459ceae0 bash