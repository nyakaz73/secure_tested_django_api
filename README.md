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
Now its probably time to create our model. Navigate to the business app and in the *models.py* file create a Customer Class follows:
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
You will probalby notice that we have an additional *PublishedManager class*, nothnig to worry about :). Now Django by default uses a Manager with the name **objects** to every Django model class. 

So if you want to create your own custom manager,you can archeve this by extending the base Manager class and add the field in your model in this case the **pubished** field.
```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')
```
So what the manager does is to simply run a query that returns the Model data(in our case Customers) where status=published.
Therefore when we query this model in the future we will be doing something like this:
```python
customers = Customer.published.all()
```
Istead of
```python
customers = Customer.objects.filter(status='published')
```

### 1b Registering the Model in Django Admin
To register the Customer model in admin
```python
from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_name','gender', 'created_by', 'created',)
    readonly_fields = ('created', )

    def full_name(self, obj):
        return obj.name + " " +obj.last_name
        
admin.site.register(Customer,CustomerAdmin)
```
Also note another trick that you can do to concart two fields into one in Django admin. You simply create and function and give an  *obj*  as a param. The obj will then be used to get the desired fields in this case **name** and **last_name**. Also note that in the list_display we then use the name of the function in this case *full_name*.  

## 2 Creating an API
Now that we have our Model Ready Lets create the CRUD API.
* First create an api app
```cmd
python manage.py startapp api
```
* Add the api module in the *settings.py* file and also add the rest_framework that we installed earlier on.
```python
...
...
    'business',
    'rest_framework', #new here
    'api',   #new here
]
```

