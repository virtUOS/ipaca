@ECHO OFF

python -m venv venv
CALL venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py read_lessons
python manage.py runserver
PAUSE