FROM ubuntu:20.04
MAINTAINER cedfactory
LABEL version="0.1"

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
COPY . /src
WORKDIR /src

RUN apt-get update
RUN apt-get install -y wget python3-pip
#RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 main:app
