#Pasos para instalar

py -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

py manage.py makemigrations

py manage.py migrate

#Para abrir el servidor

py manage.py runserver