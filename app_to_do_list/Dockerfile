FROM python:3.7.7-slim-buster

WORKDIR /web

ENV SQLALCHEMY_DATABASE_URI mysql+pymysql://
ENV CELERY_BROKER_URL amqp://
ENV CELERY_RESULT_BACKEND amqp://

ENV MAIL_SERVER smtp.yandex.ru
ENV MAIL_PORT 465
ENV MAIL_USERNAME ''
ENV MAIL_DEFAULT_SENDER ''
ENV MAIL_PASSWORD ''

EXPOSE 5000
EXPOSE 3306 33060

COPY . .

RUN pip install -r requirements.txt
RUN ls

CMD ["python", "start.py"]