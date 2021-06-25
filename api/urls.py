from django.urls import path
from api import views as api_views
from rest_framework.authtoken import views
urlpatterns = [
    path('customers/', api_views.CustomerView.as_view(), name="customer"),
    path('customers/<int:pk>/', api_views.CustomerDetailView.as_view(), name="customer-detail"),
    path('api-token-auth/', views.obtain_auth_token),
]
