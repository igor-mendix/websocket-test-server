FROM python:latest

WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
