FROM ubuntu:17.10

RUN apt update -y
RUN apt-get -y install python-pip
RUN pip install flask
RUN mkdir /flaskapp
WORKDIR /flaskapp

COPY flaskapp .

CMD ["python", "/flaskapp/app.py"]