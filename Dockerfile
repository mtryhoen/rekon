FROM microsoft/windowsservercore

RUN mkdir c:\rekon
WORKDIR c:\\rekon

RUN powershell

COPY python-3.6.3-amd64.exe .

COPY get-pip.py .

# RUN c:\rekon\python-3.6.3-amd64.exe

# RUN python c:\rekon\get-pip.py

# RUN pip install opencv-python

COPY imagedetectcol.py .

COPY haarcascade_frontalface_default.xml .

COPY createcol.py .

COPY polly.py .

# CMD ["python", "imagedetectcol.py", "haarcascade_frontalface_default.xml"]