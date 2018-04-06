FROM ubuntu:17.10

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && pip3 install --upgrade pip \
  && pip3 install boto3 \
  && pip3 install requests \
  && pip3 install numpy \
  && apt-get install -y python3-opencv

COPY cv2_ipcam.py .
COPY haarcascade_frontalface_default.xml .

CMD ["python3", "cv2_ipcam.py", "mtryhoen@gmail.com"]