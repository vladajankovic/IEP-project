FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY authentication/migration.py ./migration.py
COPY authentication/config.py ./config.py
COPY authentication/models.py ./models.py
COPY authentication/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migration.py"]