FROM python:latest

WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD ["python", "-u", "main.py"]
