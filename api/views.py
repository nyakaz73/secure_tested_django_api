from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

class CustomerView(APIView):
    def get(self, request, format=None):
        content = {'message': 'Hello, World!'}
        return Response(content)


class CustomerDetailView(APIView):
    pass