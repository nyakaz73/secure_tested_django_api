# Creating a Secure and well Tested Django RestFUL API

In this tutorial you are going to learn how you can create a secure Django API using [djangorestframework](https://www.django-rest-framework.org/) and [djangorestframework_simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).
You are also going to learn how to write unit tests for your Django API using [APIRequestFactory](). 


### Show some :heart: and :star: the repo to support the project 

## 1. Creating the API

In this section im assuming you have your virtual environment setup and ready to go. If not; you can install [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) or alternatively [pipenv](https://pypi.org/project/pipenv/) unto you machine.

* **NB** First make sure your virtual environmant is activated
* Install Django Framework
```cmd
pip install django
```
* Create Django Project
```cmd
django-admin startproject secure_tesed_django_api
```
* After the Django project has been created , will need to install a couple of dependancies that we are going to use in this project
We need to install 
```cmd
pip install djangorestframework
pip install djangorestframework_jwt
```

Now that we have our setup out of the way lets jump into the application. Navigate into your project root folder where there is the *manage.py* file.

#### We are going to create a simple CRUD businees API, where that will be using to manage the Customer Mode.


