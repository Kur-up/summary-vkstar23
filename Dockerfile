FROM python:3.10
WORKDIR /api-app

COPY ./requirements.txt /api-app/requirements.txt
RUN python -m pip install -r requirements.txt

COPY . /api-app
CMD ["python", "main.py"]