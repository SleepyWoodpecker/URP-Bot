FROM python:3.10-slim

# install all necessary dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium firefox
RUN playwright install-deps 

COPY . .

CMD ["python", "main.py"]