FROM "ubuntu:16.04"

RUN mkdir /opt/app
COPY . /opt/app/
WORKDIR /opt/app/

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install software-properties-common python3-pip libsm6 libxext6 poppler-utils -y

RUN pip3 install -r requirements.txt

RUN add-apt-repository ppa:alex-p/tesseract-ocr
RUN apt-get update

RUN apt-get install tesseract-ocr libtesseract-dev -y

RUN python3 -m nltk.downloader punkt averaged_perceptron_tagger
RUN python3 -m spacy download en

