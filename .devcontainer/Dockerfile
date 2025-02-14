FROM ubuntu:22.04
MAINTAINER cedfactory
LABEL version="0.1"

# Workaround https://unix.stackexchange.com/questions/2544/how-to-work-around-release-file-expired-problem-on-a-local-mirror
RUN echo "Acquire::Check-Valid-Until \"false\";\nAcquire::Check-Date \"false\";" | cat > /etc/apt/apt.conf.d/10no--check-valid-until

RUN apt-get update
RUN apt-get install -y wget python3-pip graphviz
#RUN python -m pip install --upgrade pip
#RUN pip install --upgrade pip

COPY requirements.txt /
RUN pip install -r requirements.txt

RUN wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib_0.6.4_amd64.deb
RUN dpkg -i ta-lib_0.6.4_amd64.deb
RUN pip install TA-Lib
#WORKDIR "/mnt"
