FROM python:3

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin

COPY store/admin/app.py ./app.py
COPY store/admin/config.py ./config.py
COPY store/admin/models.py ./models.py
COPY store/admin/functions.py ./functions.py
COPY store/admin/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
ENTRYPOINT ["python", "./app.py"]