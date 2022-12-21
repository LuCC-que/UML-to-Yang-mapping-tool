FROM python:3.10
RUN mkdir /app
WORKDIR /app


COPY requirements.txt /app/
RUN pip3 install -r requirements.txt


COPY ./src /app/


CMD [ "flask", "run", "--host", "0.0.0.0"]