# Lab project (Udemy clone)
Расположен по адресу: http://34.125.65.18/docs/

Content
* [Description](#Description)
* [Make commands](#Makecommands)
* [Installation](#Installation)
* [Docker running](#Dockerrunning)
## Description
At the moment you can use account functions only. Registration, login/logout, change and recovery your password + CRUD for your account with "IsOwnerorAdminOnly" permission. Project biuilt with using Docker (gunicorn, nginx, project_app, test cases as an individual applications with dependencies. But now i spent all quotas for buying domains on google cloud service. In future i'am going to buy domaine for that project and connect SSL for HTTPS trafic. In directory you can find nginx.conf file for https config for nginx with using docker and certbot_app as a comment for connecting and saving ssl certificate). For SSL certificate you should run docker-compose up -d nginx in deamon and after that docker-compose up -d certbot. After running certbot container you can check a result of certbot container. If you see successful status and should change nginx.conf settings for https (use nginx.conf_for using_https in project direction). HTTPS is avaliable. And you can include sertificate direction in docker volumes.

## Make commands
If you want run project without docker, you should change celery setiings:

```bash
CELERY_BROKER_URL = "redis://localhost:6379"

CELERY_RESULT_BACKEND = "redis://localhost:6379"

And in .env: POSTGRES_HOST= localhost
```

You can use following make commands:

```bash
make run
```
to run the server instead of using:
```bash
python manage.py runserver
```
##
```bash
make migrate
```
to make migrations instead of using:
```bash
python manage.py makemigrations
python manage.py migrate
```
There are other make commands which you can look up in Makefile. You don't have to use them, we made them just for your convenience
##
Also check .env_template to get more information about required data for .env.

## Installation
1. Install [celery]((https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)) + [redis](https://redis.io/)

2. Create virtual machine
```bash
python3 -m venv <venv_name>
```
3. Activate your virtual machine
```bash
. venv/bin/activate
```
4. Install all the dependencies
```bash
pip install -r requirements.txt
```
5. Make changes into database by making migrations
```bash
# First step
python manage.py makemigrations
# Second step
python manahe.py migrate
```
6. Create an admin-user
```bash
python manage.py createsuperuser
```
7. You're almost there!
```bash
python manage.py runserver
```
8. Run celery so your registered users will be able to get verification code on their email
```bash
# use second terminal
python3 -m celery -A core worker -l info
```




## Docker running
You can run server with usind docker 

1. Install Docker + Docker-compose

2. Create .env file. And create logs folder.

3. Run project
```bash
sudo docker-compose up
```