from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog', views.catalog, name='catalog'),
    path('my collection', views.my_collection, name='my collection'),
    path('profile', views.profile, name='profile'),
    path('about', views.about, name='about')
]