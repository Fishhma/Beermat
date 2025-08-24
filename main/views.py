from django.shortcuts import render
from django.http import HttpResponse
from .models import BeermatForm


def index(request):
    return render(request, 'main/index.html')


#def catalog(request):
    beermats = Beermat.objects.all()
    return render(request, 'main/catalog.html', {'beermats': beermats})


def my_collection(request):
    return render(request, 'main/my_collection.html')


def profile(request):
    return render(request, 'main/profile.html')


def about(request):
    return render(request, 'main/about.html')


def add_mat(request):
    return render(request, 'main/add_mat.html')


def catalog(request):
    beermats = BeermatForm.objects.all()

    # Получаем выбранные фильтры из URL
    country = request.GET.get("country")
    maker = request.GET.get("maker")

    if country and country != "all":
        beermats = beermats.filter(country=country)

    if maker and maker != "all":
        beermats = beermats.filter(maker=maker)

    # Список уникальных стран и брендов для выпадающих списков
    countries = BeermatForm.objects.values_list("country", flat=True).distinct()
    makers = BeermatForm.objects.values_list("maker", flat=True).distinct()

    return render(request, "main/catalog.html", {
        "beermats": beermats,
        "countries": countries,
        "makers": makers,
        "selected_country": country,
        "selected_maker": maker,
    })