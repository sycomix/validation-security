FROM python:2.7-alpine
ENV REDIS_HOST host 
ENV REDIS_PORT 6379
COPY  .  /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN sed -i 's/REDIS_HOST/'"${REDIS_HOST}"'/' /app/config.py
RUN sed -i 's/REDIS_PORT/'"${REDIS_PORT}"'/' /app/config.py
CMD  ["python", "app_model5.py"]
