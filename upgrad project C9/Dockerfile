#Window users can install docker using -->https://runnable.com/docker/install-docker-on-windows-10
#ubuntu or mac users can install docker using -->https://www.simplilearn.com/tutorials/docker-tutorial/how-to-install-docker-on-ubuntu
FROM python:3.8
WORKDIR /fastapi-app
ADD app.py .
ADD requirements.txt .
COPY ./templates ./templates
RUN python3 -m venv /opt/venv
RUN . /opt/venv/bin/activate
RUN pip install -r requirements.txt 
CMD ["python3","./app.py"]
#run your docker file from this location

#how to build docker image---> sudo docker build -t app_name .
#how to run docker image----> sudo docker run -ti app_name