from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/add/', views.submit_beermat, name='submit_beermat'),
    path('collection/', views.my_collection, name='my_collection'),
    path('profile/', views.profile, name='profile'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('profile/settings/password/', views.PasswordChange.as_view(), name='password_change'),
    path('profile/settings/password/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('about/', views.about, name='about'),

    # Auth
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),

    # Collection actions
    path('collection/add/<int:beermat_id>/', views.add_to_collection, name='add_to_collection'),
    path('collection/remove/<int:item_id>/', views.remove_from_collection, name='remove_from_collection'),
]
