FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN apt-get update;apt-get install -y libldap2-dev

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app
