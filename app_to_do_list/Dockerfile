FROM python:3.7.7-slim-buster

WORKDIR /web

ENV SQLALCHEMY_DATABASE_URI mysql+pymysql://test1:Test1_2020@localhost/crud
ENV CELERY_BROKER_URL amqp://haraleks:123456@localhost:5672/vhost
ENV CELERY_RESULT_BACKEND amqp://haraleks:123456@localhost:5672/vhost

ENV MAIL_SERVER smtp.yandex.ru
ENV MAIL_PORT 465
ENV MAIL_USE_TLS False
ENV MAIL_USE_SSL True
ENV MAIL_USERNAME flask.crud@yandex.ru
ENV MAIL_DEFAULT_SENDER flask.crud@yandex.ru
ENV MAIL_PASSWORD Crud2020


EXPOSE 5000
EXPOSE 3306 33060

COPY . .


RUN pip install -r requirements.txt
RUN ls

CMD ["python", "start.py"]