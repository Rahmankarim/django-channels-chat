[![Total alerts](https://img.shields.io/lgtm/alerts/g/tiagoarasilva/django-channels-chat.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tiagoarasilva/django-channels-chat/alerts/)

# Django Channels Chat

- This is supporting [Django Channels](https://channels.readthedocs.io/en/stable/index.html).
- Read more about this [here](https://channels.readthedocs.io/en/stable/index.html)


# Notes 
- Simple chat built using Django channels, Postgres/Sqlite3 and Redis.
- This is for testing purposes and to show the simplicity of doing it and of course, it can be changed to be 1 to 1 chat with request users
- This repo will be updated accordingly and as needed


## Requirements
- Python 3.6+
- Virtual environment
- Docker
- Django 2+


## Installation
To install the requirements on development environment, just run

```shell script
pip install -r requirements/development.txt 
```

For postgres use, you should run this (or similar)
```shell script
sudo apt-get update
sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib
```

Or you can just uncomment inside `canal/databases.py` the sqlite3 configuration and ignore the postgres version

## Booting up

- Firstly, you should run `docker-compose up` to boot the docker resources needed
- Run the current migrations by typing `make migrate` or `python canal/manage.py migrate`
- There are 2 ways of starting the project, one is with a Makefile command and the second without it

With Makefile command:
```shell script
make run
```

* Without Makefile Command
```shell script
python canal/manage.py runserver
```
or inside the canal module
```shell script
python manage.py runserver
```

You should see something similar to

```shell script
Performing system checks...

System check identified no issues (0 silenced).
December 11, 2019 - 11:11:46
Django version 3.0, using settings 'canal.settings'
Starting ASGI/Channels version 2.3.1 development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

The endpoint for the chat is `http://localhost:8000/chat/` where a string for the room should be passed. Do the
same thing in a different browser tab/window and start chatting through it

## Run the tests
```shell script
make tests
```
