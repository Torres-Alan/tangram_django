from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def hello(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def about(request):
    return HttpResponse("About Us")