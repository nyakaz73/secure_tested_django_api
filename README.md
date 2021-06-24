# Creating a Secure and well Tested Django RestFUL API

In this tutorial you are going to learn how you can create a secure Django API using [djangorestframework](https://www.django-rest-framework.org/) and [djangorestframework_simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).
You are also going to learn how to write unit tests for your Django API using [APIRequestFactory](). 


### Show some :heart: and :star: the repo to support the project 

## 1. CREATING THE API

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

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return "{} {}".format(self.name,self.last_name)

```
You will probalby notice that we have an additional *PublishedManager class*, nothnig to worry about :). Now Django by default uses a Manager with the name **objects** to every Django model class. 

So if you want to create your own custom manager,you can archiexve this by extending the base Manager class and add the field in your model in this case the **pubished** field.
```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')
```
So what this manager does is to simply run a query that returns the Model data(in our case Customers) where the status=published.
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
Also note another trick that you can do to concat two fields in Django admin. You simply create a function and give an  *obj*  as a param. The obj will then be used to get the desired fields in this case **name** and **last_name**. Also note that in the list_display tuple we then use the name of the function in this case *full_name*.  

### 1c CRUD API
Now that we have our Model Ready Lets create the CRUD API.
* First create an api app
```cmd
python manage.py startapp api
```
* Add the api module in the *settings.py* file and also add the **rest_framework** that we installed earlier on.
```python
...
...
    'business',
    'rest_framework', #new here
    'api',   #new here
]
```
#### 1c1 API URLS
* Now include the **api** app in the base *urls.py* file where there is the settings.py file.
```python
from django.contrib import admin
from django.urls import path, include #new here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), #new here
]
```

* Finally create a *urls.py* file the **api** app and add the following routes.
```python
from django.urls import path
from api import views as api_views

urlpatterns = [
    path('customers/', api_views.CustomerView.as_view(), name="customer"),
    path('customers/<int:pk>', api_views.CustomerDetailView.as_view(), name="customer-detail")
]

```
In the above snippet we have created the customer routes with views **CustomerView** and **CustomerDetailView** which we are going to create shortly.
The **CustomerView** is essentially going to handle our **get all** *get* request and **save** *post* request then;
The **CustomerDetailView** is going to handle our *get*, *put and delete* requests.

#### 1c2  API Views
Navigate to the *views.py* inside the **app** folder and add the following code. 
```python
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from business.models import Customer
from api.serializers import CustomerSerializer
from rest_framework import status
from django.http import Http404
from functools import wraps
class CustomerView(APIView):
    def get(self, request, format=None):
        customers = Customer.published.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    
    def post(self,request,format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


def resource_checker(model):
    def check_entity(fun):
        @wraps(fun)
        def inner_fun(*args, **kwargs):
            try:
                x = fun(*args, **kwargs)
                return x
            except model.DoesNotExist:
                return Response({'message': 'Not Found'}, status=status.HTTP_204_NO_CONTENT)
        return inner_fun
    return check_entity

class CustomerDetailView(APIView):
    
    @resource_checker(Customer)
    def get(self,request,pk, format=None):
        customer = Customer.published.get(pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    @resource_checker(Customer)
    def put(self,request,pk, format=None):
        customer = Customer.published.get(pk=pk)
        serializer = CustomerSerializer(customer,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @resource_checker(Customer)
    def delete(self,request, pk, format=None):
        customer = Customer.published.get(pk=pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
```
Now Lets break this code down
* **CustomerView**
As mentioned above the CustomerView is going to handle our get all request and  post request by extending the rest_framework APIView.
Note how we are now making use of the Manager that we creating in the Customer Model.
```python
...
customers = Customer.published.all()
...
```
Here we are simply getting all Customers that has the status= published.
Also note that we  have a **CustomerSerializer** which we will create shortly with **many=True** meaning Serializer has to searialize the  List of Objects.


* **CustomerDetailView**
Is going to handle the rest of our CRUD request operations, ie *get, put and delete* requests.
Since we are going to perform  a queryset that is going to get a specific Customer by the pk, for the rest of the requests; we need  a way of handling the model **DoesNotExist** exception which is thrown if you query against a Customer that is not in the database.

* There are multiple ways of handling such a scenario , like for instance one way would be to *try catch* every request in this view, but the donwfall with this approach is the bottleneck of uncessary repetition of code.

* To solve this we can make use of a python [decorator](https://www.python.org/dev/peps/pep-0318/) pattern that lets you annoatate every function request which will handle the model DoesNotExist exception.
See code below
```python
def resource_checker(model):
    def check_entity(fun):
        @wraps(fun)
        def inner_fun(*args, **kwargs):
            try:
                x = fun(*args, **kwargs)
                return x
            except model.DoesNotExist:
                return Response({'message': 'Not Found'}, status=status.HTTP_204_NO_CONTENT)
        return inner_fun
    return check_entity
```
The above nippet checks of a Model with a given pk exists, if it does it runs the request via
```python
x = fun(*args, **kwargs)
```
Else if the resource does not exist it then returns a Not Found exception.
```python
return Response({'message': 'Not Found'}, status=status.HTTP_204_NO_CONTENT)
```
A **decorator** is a python concept that lets you run a function within another function thus providing some abstrction in code that lets you use same code base in different scenarios or **alter the behavior of a function or a class**.
Since we are going to pass a parameter in our decorate ie a Class Model we need some form of Factory Function that will take the param and later send it down the chain with other func params

Im not going to in detail about python decorators as it is a wide concept. 

#### 1c3 API CustomerSerializer
Lets create CustomerSerializer class
* Create a file called ***serializers.py*** in  the **api** folder with the following code

```python
from rest_framework import serializers
from business.models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__' 
        
```
* To create a rest serializer class you need to extend the ModelSerializer base.


#### 1c4 Running app
From this stage everything should be fine now you can go a ahead and run your migrations.
```cmd
python manage.py makemigrations 
python manage.py migrate
```
You can even go ahead and test with postman to see if the application is behaving as expected.
* **Note** we will write some unit tests in the last section of this tutorial so stay tuned :)

##### Examples
POST request
<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/getrequestz.png" width="100%" height=auto />

## 2 SECURING THE API
