# Beermat Collector

A simple Django app to catalog and collect beer coasters (beermats).

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Features

- Browse a catalog of beermats
- Submit new beermats (admin approval required)
- Add beermats to user collection
- Admin-managed news/announcements on the home page

## Notes

- Uploaded images are stored in `media/`
- Only JPEG/PNG uploads are allowed
