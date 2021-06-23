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

#### We are going to create a simple CRUD businees API, that will be using to manage a Customer Model.

* Create New app called business

```cmd
python manage.py startapp business
```
After creating the business app make sure to add the module in the *settings.py* file under installed app.

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'business', #new here
]
```

### 1a. Customer Model
Now its probably time to create our model. Navigate to the business app and in the *models.py* file create a Customer Classas follows:
```python
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')

class Customer(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F','Female'),
        ('I', 'Intersex')
    )
    title = models.CharField(max_length=250, null=False)
    name = models.CharField( max_length=250)
    last_name = models.CharField(max_length=250)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_by = models.ForeignKey(
        User, related_name='created_by',  editable=False, on_delete=models.PROTECT, default=1)
    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')

    published = PublishedManager()

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return "{} {}".format(self.name,self.last_name)

```

