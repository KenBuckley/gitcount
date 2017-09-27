FROM ubuntu
MAINTAINER Name kenneth.buckley@gmail.com

#Update
RUN apt-get update -qq && apt-get install -y python3 python3-setuptools python3-pip 
RUN easy_install3 pip

COPY . /src 

# Install app dependencies
RUN pip3 install -r /src/requirements.txt

EXPOSE 8080
# Set the default command
ENTRYPOINT ["python3", "/src/gitcount.py"] 
