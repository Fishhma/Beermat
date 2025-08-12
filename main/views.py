from django.shortcuts import render
from django.http import HttpResponse
from .models import Beermat


def index(request):
    return render(request, 'main/index.html')


def catalog(request):
    beermats = Beermat.objects.all()
    return render(request, 'main/catalog.html', {'beermats': beermats})


def my_collection(request):
    return render(request, 'main/my_collection.html')


def profile(request):
    return render(request, 'main/profile.html')


def about(request):
    return render(request, 'main/about.html')