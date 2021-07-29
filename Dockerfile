FROM python:3.9-slim


ADD ./python_requirements.txt /
RUN python3 -m pip install -r python_requirements.txt

ADD ./01_construct_features.py /
ADD ./config.py /
ADD ./construct_data.sh /
ADD ./functions.py /
ADD ./predict_url.py /
ADD ./server.py /
ADD ./inputSegments3.csv /
ADD ./FinalData.csv /

ADD ./stopwords_extended.txt /
ADD ./word_frequency_2021-07-29.picle /

RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader wordnet
RUN python3 -m nltk.downloader stopwords
CMD [ "python3", "-u", "./server.py" ]
