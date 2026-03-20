FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "beermat_site.wsgi:application", "--bind", "0.0.0.0:8000"]