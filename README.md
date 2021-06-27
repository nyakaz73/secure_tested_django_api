# Creating a Secure and well Tested Django RestFUL API

In this tutorial you are going to learn how you can create a secure Django API using [djangorestframework](https://www.django-rest-framework.org/) and [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).
You are also going to learn how to write unit tests for your Django API using [APITestCase](). 


### Show some :heart: and :star: the repo to support the project 

# Get Started
* This tutorial is divided it into three sections:

* 1. CREATING THE REST API
* 2. SECURING THE API
* 3. REST API UNIT TESTING

## 1. CREATING THE REST API

In this section i'm assuming you have your virtual environment setup and ready to go. If not; you can install [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) or alternatively [pipenv](https://pypi.org/project/pipenv/) unto you machine.

* **NB** First make sure your virtual environmant is activated
* Install Django Framework
```cmd
pip install django
```
* Create Django Project
```cmd
django-admin startproject secure_tesed_django_api
```
* After the Django project has been created , you will need to install a couple of dependancies that we are going to use in this project
We need to install 
```cmd
pip install djangorestframework
pip install djangorestframework-simplejwt
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
* Also remember to create a **superuser**

```cmd
python manage.py makemigrations 
python manage.py migrate
python manage.py createsuperuser
```

You can even go ahead and test with postman to see if the application is behaving as expected.
* **Note** we will write some unit tests in the last section of this tutorial so stay tuned :)

##### Examples
POST request
<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/getrequestz.png" width="100%" height=auto />

## 2 SECURING THE API
In this section we are going to use djangorestframework and djangorestframework_simplejwt that we installed earlier to secure our end points.

Go to the **api/views.py** file and add the permission classes as below:
```python
...
from rest_framework.permissions import IsAuthenticated  #new here
class CustomerView(APIView):
    permission_classes = (IsAuthenticated,) #new here
    def get(self, request, format=None):
        customers = Customer.published.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    ...
    ...
...
...
class CustomerDetailView(APIView):
    permission_classes = (IsAuthenticated,)#new here
    @resource_checker(Customer)
    ...
    ...
```
At this stage both of your views should be protected if you try to hit one of the end points eg get /customers 
<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/terminalcurl.png" width="100%" height=auto />
You probably notice you are now getting a HTTP 403 Forbidden error, lets now implement the token authentication so that we will be able to hit our end points.

### 2a REST TokenAuthentication
The [djangorestframework](https://www.django-rest-framework.org/) comes with a token based mechanism for authenticating authorising access to secured end point.

Lets start by adding a couple of configurations to the **settings.py** file.
* Add **rest_framework.authtoken** to **INSTALLED_APPS** and **TokenAuthentication** to **REST_FRAMEWORK**.
```python
...
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'business',
    'rest_framework',
    'api',
    'rest_framework.authtoken', #new here
]

REST_FRAMEWORK = {           #new here
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', 
    ],
}
...
```
After adding the configurations make sure you migrate to apply the **authtoken** tables.

```cmd
python manage.py migrate
```

#### Generate Token
Now to  make successful requests we need to pass an **Authorization Header** to our request with a **Token**.
* To generate a token we need an account that we created earlier if not just quickly create one:

```cmd
python manage.py createsuper --username admin --email tafadzwalnyamukapa@gmail.com
```
* You can now generate your token by running the django **drf_create_token** command:
<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/tokengen.png" width="100%" height=auto />
You should now be able to see a string like this

```cmd
Generated token 73d29cb34e8a972741462fa3022935e43c18a247 for user admin
```
* Now lets run the get /customers request that we tried earlier on with curl:

```cmd
curl http://localhost:8000/api/customers/ -H 'Authorization: Token 73d29cb34e8a972741462fa3022935e43c18a247' | json_pp
```
<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/customerreq.png" width="100%" height=auto />
Now we have successfully retrieved our list of customers. 

* **NB** Note that you need to pass the token with a Token value in the Authorization Header

Now this works just fine but if a client want to be able to get the token and run the exposed secured end points ,there should be a way of doing that. Not to worry *djangorestframework* comes with a helper end point that should let the client provide their credentials ie **username and password** and make a **POST** request in order to retrieve the token.

We are going to use **obtain_auth_token** view to archieve the above scenario.


#### Client Requesting Token
Navigate to  **api/urls.py** file and add the following route:
```python
from django.urls import path
from api import views as api_views
from rest_framework.authtoken import views # new here
urlpatterns = [
    path('customers/', api_views.CustomerView.as_view(), name="customer"),
    path('customers/<int:pk>/', api_views.CustomerDetailView.as_view(), name="customer-detail"),
    path('api-token-auth/', views.obtain_auth_token), #new here
]
```
Now the client should be a be able to make a post request to ***/api/api-token-auth*** to obtain the Authorization token:
Request:

```cmd
curl -d "username=admin&password=admin12#" -X POST http://localhost:8000/api/api-token-auth/
```
<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/userpass.png" width="100%" height=auto />
Response:

```cmd
{"token":"73d29cb34e8a972741462fa3022935e43c18a247"}
```

* Now at this point the client has succssfully obtained the token,its now up to them to save it in **localStorage**,or **sessionCookies** or any other state manager, in order to make the rest of the requests.


### 2b JWT Authorization and Iformation Exchange
* Up to this point we have been using the REST Token for,authorization, while this works fine, there is another exellent way that we can use to archive this that is more secure when transimitting information between two parties ie **JWT (Json Web Token)**.
* This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the **HMAC** algorithm) or a ***public/private key pair*** using **RSA** or **ECDSA**.

### JSON Web Token structure?
* The JWT consits of a ***Header.Payload.Signature*** in that order.
```cmd
xxxx.yyyy.zzzz
```
Simple JWT:
```cmd
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU
```

#### Header
* The header typically consists of two parts: the type of the token, which is JWT, and the signing algorithm being used, such as HMAC SHA256 or RSA.
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
#### Payload
* The second part of the token is the payload, which contains the claims. Claims are statements about an entity (typically, the user) and additional data. There are three types of claims: registered, public, and private claims.
```json
"token_type": "access",
  "exp": 1543828431,
  "jti": "7f5997b7150d46579dc2b49167097e7b",
  "user_id": 5cc
```
#### Signature

* To create the signature part you have to take the encoded header, the encoded payload, a secret, the algorithm specified in the header, and sign that.

```json
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

* To get started with djangorestframework-simplejwt

Navigate to ***settings.py***, add **rest_framework_simplejwt.authentication.JWTAuthentication** to the list of authentication classes:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', 
        'rest_framework_simplejwt.authentication.JWTAuthentication', #new here
    ],
}
```

* Also, in **api/urls.py** file include routes for Simple JWT’s ***TokenObtainPairView*** and ***TokenRefreshView*** views:

```python
from django.urls import path
from api import views as api_views
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import ( #new her
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('customers/', api_views.CustomerView.as_view(), name="customer"),
    path('customers/<int:pk>/', api_views.CustomerDetailView.as_view(), name="customer-detail"),
    path('api-token-auth/', views.obtain_auth_token),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), #new here
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  #new here
]

```
#### Obtain JWT Token

* To obtain the token you need to make a *POST* request to the ***/api/token/*** end point on the **TokenObtainPairView**:
Request:

```cmd
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123#"}' http://localhost:8000/api/token/
```
Response:

```json
{
   "access" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI0NzAxMzY3LCJqdGkiOiIwNmMyNjU0NjQyOWU0MThkODUzYzljZDViOTUyYmYyZSIsInVzZXJfaWQiOjF9.nW_bq87ob0PT5vm8uQ4ZsczO5jIZxtD6XTb1vQdz7_w",
   "refresh" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyNDc4NzI2MywianRpIjoiM2Q0NzdhZmZiOGFhNDRhZjkzMmJhZDI0NjlhNmYwZWYiLCJ1c2VyX2lkIjoxfQ.s4rOL75ddLGCFnLt38Kwa3Du1O-j5Z7YC0cx0aetW4Q"
}
```

* You can notice that in our response we got the **access** and **referesh** tokens. 
* We are going to access the secured endpoint eg ***/api/customers/*** by using rhe aceess token. 

```cmd
curl http://localhost:8000/api/customers/ -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI0NzAxMzY3LCJqdGkiOiIwNmMyNjU0NjQyOWU0MThkODUzYzljZDViOTUyYmYyZSIsInVzZXJfaWQiOjF9.nW_bq87ob0PT5vm8uQ4ZsczO5jIZxtD6XTb1vQdz7_w' | json_pp
```
* **NB** Notice that we have used **Bearer** keyword instead of *Token* in our request Authorization Header.

<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/jwtreq.png" width="100%" height=auto />

* The access token by default is valid for **5 minutes** . After the expiry time has elapsed you cant use the same token else you will get an "Token is invalid or expired".
```json
{
   "code" : "token_not_valid",
   "messages" : [
      {
         "token_class" : "AccessToken",
         "token_type" : "access",
         "message" : "Token is invalid or expired"
      }
   ],
   "detail" : "Given token not valid for any token type"
}
```
* To get a new access token you need to make a POST request with refresh token as data  **/api/token/refresh/**,  ***TokenRefreshView***  
* The refresh token is valid for 24HRS.
```cmd
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyNDc4NzI2MywianRpIjoiM2Q0NzdhZmZiOGFhNDRhZjkzMmJhZDI0NjlhNmYwZWYiLCJ1c2VyX2lkIjoxfQ.s4rOL75ddLGCFnLt38Kwa3Du1O-j5Z7YC0cx0aetW4Q"}' \
  http://localhost:8000/api/token/refresh/
```
<img src="https://github.com/nyakaz73/secure_tested_django_api/raw/master/refresh.png" width="100%" height=auto />

* To configure token behavior eg lifetime, add the SIMPLE_JWT configurations in **settings.py**:
```python
from datetime import timedelta

...

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),   #update here for acess token
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1), # update here for refresh token
}
```

## 3. REST API UNIT TESTING

* In this section we are going to look at how to run unit test on django restful api.
* We are going to use the restframework **APITestCase** and the **APIClient** for our **CRUD** requests.

* To begin delete the ***/api/tests.py*** file in the **api** folder.
```cmd
rm /api/tests.py
```
* Created a new folder inside the **/api** folder called tests
```cmd
mkdir /api/tests
```
* Navigate to the newly created tests folder.
```cmd
cd /api/tests/
```
* Create a test file ***test_customer_api.py***
```cmd
cat test_customer_api.py
```
* Create an __init__.py inside the same */tests* folder so that the django test runner will be able to pick our test file.
```cmd
cat __init__.py
```

* Now add the following snippet inside the newly created ***test_customer_api.py*** file.
```python
from django.urls import reverse,  resolve
from django.test import SimpleTestCase
from api.views import CustomerView
class ApiUrlsTests(SimpleTestCase):

    def test_get_customers_is_resolved(self):
        url = reverse('customer')
        self.assertEquals(resolve(url).func.view_class, CustomerView)
```
* Before we jump to the restframework **APITestCase** lets start with this django urls unit testing.
* The above code simply tests the get ***/api/customers/*** url to see if it is firing the correct ViewClass.
* The default behavior of the test utility is to find all the test cases (that is, subclasses of unittest.TestCase) in any file whose name begins with **test**

Here we are using the django reverse function to get the absolute url of the path. 
We then asset the resolved url function view_class name against the name of the Class Viwew that we want it to trigger.

* To run the test  run the test command (*./manage.py test <app-name>*) with the name of  app. If you dont add the name of the app the test runner will look for all apps in the project and run the test cases if there are any.
```cmd
python manage.py test api

System check identified no issues (0 silenced).
.
----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```
The test successfully runs 1 test and it passed.
* Now lets continue with djangorestframework tests.

#### APITestCase
The REST framework uses incles test case classes , that mirror the existing Django test cases classes. They include
* APISimpleTestCase
* APITransactionTestCase
* APITestCase
* APILiveServerTestCase


```python
from django.urls import path, reverse, include, resolve
from django.test import SimpleTestCase
from api.views import CustomerView
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.views import APIView


class ApiUrlsTests(SimpleTestCase):

    def test_get_customers_is_resolved(self):
        url = reverse('customer')
        self.assertEquals(resolve(url).func.view_class, CustomerView)


class CustomerAPIViewTests(APITestCase): #new here
    customers_url = reverse("customer")

    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='admin')
        self.token = Token.objects.create(user=self.user)
        #self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_customers_authenticated(self):
        response = self.client.get(self.customers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_customers_un_authenticated(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.customers_url)
        self.assertEquals(response.status_code, 401)

    def test_post_customer_authenticated(self):
        data = {
            "title": "Mr",
            "name": "Peter",
            "last_name": "Parkerz",
            "gender": "M",
            "status": "published"
        }
        response = self.client.post(self.customers_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 8)
        
class CustomerDetailAPIViewTests(APITestCase):
    customer_url = reverse('customer-detail', args=[1])
    customers_url = reverse("customer")

    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='admin')
        self.token = Token.objects.create(user=self.user)
        #self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Saving customer
        data = {
            "title": "Mrs",
            "name": "Johnson",
            "last_name": "MOrisee",
            "gender": "F",
            "status": "published"
        }
        self.client.post(
            self.customers_url, data, format='json')

    def test_get_customer_autheticated(self):
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Johnson')

    def test_get_customer_un_authenticated(self):
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, 401)

    def test_delete_customer_authenticated(self):
        response = self.client.delete(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

```

Alright now the code has extended a bit, but nothing to worry about :), lets break it down.

#### CustomerAPIViewTests
Now in this case we want to test the CustomerView that does our **get** all and **post** request.

* Since we are now working with the database we need to extend an appropriate test case in our case an ***APITestCase***.
```python
class CustomerAPIViewTests(APITestCase):
```
* We then  use the django reverse function to get the absolute url by name "customer".
```python
customers_url = reverse("customer")
```self.client.force_authenticate(user=None, token=None)
    response = self.client.get(self.customer_url)
    self.assertEqual(response.status_code, 401)

def test_delete_customer_authenticated(self):
    response = self.client.delete(self.customer_url)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)tion including user creation and token signing in are going to be perfomed in the setUp function.
* The setUp method will only be run once on each test case.

```python
def setUp(self):
    self.user = User.objects.create_user(
        username='admin', password='admin')
    self.token = Token.objects.create(user=self.user)
    #self.client = APIClient()
    self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
```
* Inside the function we are creating the user, and the token. The django test runner sets  up a  volatile DB on every run and tears it down after each test case, and with that in mind we dont necessarily need a ***tearDown*** function.

* The **APITestCase** comes with a **client** from the ***APIClient*** class which we then use to configure our **request** Headers using the **credentials method**.

* Setup the request Authorization Header with a token to the client:
```pythonargumenttatus.HTTP_200_OK)
```
* Here we are making a get customers request to the /api/customers/ endpoint.
```python
response = self.client.get(self.customers_url)
```

* We are using assetEqual to make our declative statements, for our test.
```python
self.assertEqual(response.status_code, status.HTTP_200_OK)
```

* Here we are declaring /asserting that the response's status_code == 200.

* Now the above test case was for an **authenticated** client , now lets test an un-authenticated client and see if we attain the desired results.

```python
 self.client.force_authenticate(user=None, token=None)
```
* To bypass authentication entirely for this test case we use the force_authenticate function on our **client** and assign the user or token to None.

* We then assert a **401** response on the status_code.

* THe post request , we are using the same client to make a post request, and assert a **201** status Created.


#### CustomerDetailAPIViewTests
 In this test class we are doing almost everything that we have covered above expect for a few things. Lets take a look

 ```python
customer_url = reverse('customer-detail', args=[1])
 ```
 You will probably notice that our reverse function is now a bit different , this is because the **customer-detail** path take an argument pk See urls.py code below:
 ```python
 ...
  path('customers/<int:pk>/', api_views.CustomerDetailView.as_view(), name="customer-detail"),
  ...
  ```
  So we then pass an argument in the args list, in this case we are passing a 1.

  * Since we want to perfom **get**, **delete**,**put**  requests we need to pre-insert a customer  in the DB during the setUp , since the customer is going to be used by the rest of the test cases.
* Also note that this is now a different TestCalss so we need to crete a user , token and pass the Authorization token to the client request Header.
Pre-Inserting Customer
```python
self.client.post(self.customers_url, data, format='json')
```

**GET** and **DELETE** requests

```python
...
def test_get_customer_autheticated(self):
    response = self.client.get(self.customer_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['name'], 'Johnson')

def test_get_customer_un_authenticated(self):
    self.client.force_authenticate(user=None, token=None)
    response = self.client.get(self.customer_url)
    self.assertEqual(response.status_code, 401)

def test_delete_customer_authenticated(self):
    response = self.client.delete(self.customer_url)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
...
```
In the get by id /api/customer/1 request , we are asserting that the response has  a name == 'Johnson':
```python
self.assertEqual(response.data['name'], 'Johnson')
```

In the delete request /api/customers/1 ,we are asserting that the response will return a 204 No content Found status_code.

* Now Finally Run your tests:
```cmd
python manage.py test api

Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 7 tests in 1.447s

OK
Destroying test database for alias 'default'...
```

* If you have 7 passed tests then CONGRATULATIONS you have created your REST API UNIT TESTING.

* **NB** As a rule of thumb make sure you mess around with the assertions, just to make sure your tests are working as Expected.

END !!

* If there is anything you feel i should have covered or improve ,Please let me know in the comments section below.

Thank you for taking your time in reading this article.

KINDLY FORK AND STAR THE [REPO](https://github.com/nyakaz73/secure_tested_django_api) TO SUPPORT THIS PROJECT :)

### Source Code Git repo
The source code of this [repo](https://github.com/nyakaz73/secure_tested_django_api)
### Pull Requests
I Welcome and i encourage all Pull Requests....
## Created and Maintained by
* Author: [Tafadzwa Lameck Nyamukapa](https://github.com/nyakaz73) 
* Email:  [tafadzwalnyamukapa@gmail.com]
* Youtube Channel: [Stack{Dev}](https://www.youtube.com/channel/UCacNBWW7T2j_St593VHvulg)
* Open for any collaborations and Remote Work!!
* Happy Coding!!

### License

```
MIT License

Copyright (c) 2021 Tafadzwa Lameck Nyamukapa

```