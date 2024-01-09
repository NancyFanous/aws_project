FROM python:3.8-slim
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY YOURPUBLIC.pem .

CMD ["python", "app.py"]

