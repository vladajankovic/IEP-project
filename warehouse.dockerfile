FROM python:3

RUN mkdir -p /opt/src/warehouse
WORKDIR /opt/src/warehouse

COPY store/warehouse/app.py ./app.py
COPY store/warehouse/config.py ./config.py
COPY store/warehouse/functions.py ./functions.py
COPY store/warehouse/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
ENTRYPOINT ["python", "./app.py"]