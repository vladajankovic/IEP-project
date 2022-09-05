FROM python:3

RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

COPY store/daemon/app.py ./app.py
COPY store/daemon/config.py ./config.py
COPY store/daemon/models.py ./models.py
COPY store/daemon/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./app.py"]