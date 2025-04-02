FROM python:3.12

COPY ./grounder  /grounder

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt
