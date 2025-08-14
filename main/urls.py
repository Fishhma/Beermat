from django.urls import path, include
from django.contrib import admin
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog', views.catalog, name='catalog'),
    path('my collection', views.my_collection, name='my collection'),
    path('profile', views.profile, name='profile'),
    path('about', views.about, name='about')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)