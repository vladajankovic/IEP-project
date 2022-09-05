FROM python:3

RUN mkdir -p /opt/src/buyer
WORKDIR /opt/src/buyer

COPY store/buyer/app.py ./app.py
COPY store/buyer/config.py ./config.py
COPY store/buyer/models.py ./models.py
COPY store/buyer/functions.py ./functions.py
COPY store/buyer/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
ENTRYPOINT ["python", "./app.py"]