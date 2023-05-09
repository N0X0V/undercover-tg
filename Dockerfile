FROM python:3.11-bullseye
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT python3.11 main.py
EXPOSE 80
