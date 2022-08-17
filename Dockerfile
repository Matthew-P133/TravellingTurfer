FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code



# dependencies
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt



# copy project code
COPY . /code
EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000