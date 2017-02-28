FROM python:3.4

ADD . /code/

WORKDIR /code/

RUN pip install -r requirements/prod.txt \
    && pip install https://github.com/benoitc/gunicorn/tarball/master \
    && pip install --no-deps -e .

EXPOSE 8080

CMD ["gunicorn", "-c", "/code/docker/gunicorn_conf.py", "shortener_url.wsgi:create_app()"]


