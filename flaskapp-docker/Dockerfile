FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install gunicorn3 -y

COPY flaskapp/requirements.txt requirements.txt
COPY flaskapp /opt/

RUN mkdir ~/.aws
COPY ../../credentials ~/.aws/credentials

RUN pip3 install -r requirements.txt
WORKDIR /opt/

CMD ["gunicorn3","-b","0.0.0.0:8000","app:app","--workers=5"]
