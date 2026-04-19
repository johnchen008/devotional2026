# Full Daily Devotional Django System

This project includes:
- dynamic daily pages by date
- separate CSS file
- CSV import command
- banner image switching
- Bible reading links
- previous / next navigation
- Django admin support

## Included files
- `PDF/devotions_jan_jun_2026_english.csv`
- `static/images/picture1.jpg`
- `static/images/picture2.jpg`
- `static/images/picture3.jpg`
- `static/images/picture4.jpg`

## Setup
```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py import_devotions_csv "PDF/devotions_jan_jun_2026_english.csv" --overwrite
python manage.py runserver
```

## PythonAnywhere
```bash
pip install --user -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py import_devotions_csv "PDF/devotions_jan_jun_2026_english.csv" --overwrite
python manage.py collectstatic --noinput
```
