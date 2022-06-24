FROM python:3.10

WORKDIR /code

ADD ./requirements.txt /temp/requirements.txt

RUN pip install -r /temp/requirements.txt

ADD . /code

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]