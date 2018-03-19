FROM python:2.7-alpine
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
ENTRYPOINT ["celery"]
CMD ["worker", "-A validation_task_manager  --loglevel=info"]