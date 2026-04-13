from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.db.models import IntegerField, OuterRef, Subquery, Value
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.urls import reverse

from .forms import BeermatSubmissionForm, ProfileForm, UserUpdateForm
from .models import Beermat, CollectionItem, NewsItem


class LoginView(DjangoLoginView):
    template_name = 'beermats/login.html'


class LogoutView(DjangoLogoutView):
    http_method_names = ['get', 'post', 'options']
    next_page = 'home'
    template_name = 'beermats/logged_out.html'

    def get_next_page(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return resolve_url(next_url)
        return super().get_next_page()


class PasswordChange(PasswordChangeView):
    template_name = 'beermats/password_change_form.html'
    success_url = '/profile/settings/password/done/'


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'beermats/password_change_done.html'


def home(request):
    approved_beermats = Beermat.objects.filter(approved=True)
    recent_beermats = approved_beermats.order_by('-approved_at')[:5]
    news_items = NewsItem.objects.filter(published=True).order_by('-published_at')[:5]
    total_beermats = approved_beermats.count()
    total_breweries = approved_beermats.filter(brewery__gt='').values('brewery').distinct().count()
    total_countries = approved_beermats.filter(country__gt='').values('country').distinct().count()
    total_brands = approved_beermats.filter(beer_name__gt='').values('beer_name').distinct().count()
    return render(
        request,
        'beermats/home.html',
        {
            'recent_beermats': recent_beermats,
            'news_items': news_items,
            'total_beermats': total_beermats,
            'total_breweries': total_breweries,
            'total_countries': total_countries,
            'total_brands': total_brands,
        },
    )


def about(request):
    return render(request, 'beermats/about.html')


def catalog(request):
    base_beermats = Beermat.objects.filter(approved=True)
    selected_beer = request.GET.get('beer', 'all')
    selected_brewery = request.GET.get('brewery', 'all')
    selected_country = request.GET.get('country', 'all')

    if request.user.is_authenticated:
        beermats = base_beermats.annotate(
            user_collection_id=Subquery(
                CollectionItem.objects.filter(user=request.user, beermat=OuterRef('pk'))
                .values('id')[:1]
            )
        )
    else:
        beermats = base_beermats.annotate(user_collection_id=Value(None, output_field=IntegerField()))

    countries = base_beermats
    if selected_beer and selected_beer != 'all':
        countries = countries.filter(beer_name=selected_beer)
    if selected_brewery and selected_brewery != 'all':
        countries = countries.filter(brewery=selected_brewery)
    countries = (
        countries
        .filter(country__gt='')
        .order_by('country')
        .values_list('country', flat=True)
        .distinct()
    )

    beers = base_beermats
    if selected_country and selected_country != 'all':
        beers = beers.filter(country=selected_country)
    if selected_brewery and selected_brewery != 'all':
        beers = beers.filter(brewery=selected_brewery)
    beers = (
        beers
        .filter(beer_name__gt='')
        .order_by('beer_name')
        .values_list('beer_name', flat=True)
        .distinct()
    )

    breweries = base_beermats
    if selected_country and selected_country != 'all':
        breweries = breweries.filter(country=selected_country)
    if selected_beer and selected_beer != 'all':
        breweries = breweries.filter(beer_name=selected_beer)
    breweries = (
        breweries
        .filter(brewery__gt='')
        .order_by('brewery')
        .values_list('brewery', flat=True)
        .distinct()
    )
    
    if selected_country and selected_country != 'all':
        beermats = beermats.filter(country=selected_country)
    if selected_beer and selected_beer != 'all':
        beermats = beermats.filter(beer_name=selected_beer)
    if selected_brewery and selected_brewery != 'all':
        beermats = beermats.filter(brewery=selected_brewery)

    catalog_total_beermats = beermats.count()
    catalog_total_countries = beermats.filter(country__gt='').values('country').distinct().count()
    catalog_total_brands = beermats.filter(beer_name__gt='').values('beer_name').distinct().count()
    catalog_total_breweries = beermats.filter(brewery__gt='').values('brewery').distinct().count()

    return render(
        request,
        'beermats/catalog.html',
        {
            'beermats': beermats,
            'countries': countries,
            'beers': beers,
            'breweries': breweries,
            'selected_country': selected_country,
            'selected_beer': selected_beer,
            'selected_brewery': selected_brewery,
            'catalog_total_beermats': catalog_total_beermats,
            'catalog_total_countries': catalog_total_countries,
            'catalog_total_brands': catalog_total_brands,
            'catalog_total_breweries': catalog_total_breweries,
        },
    )


@login_required
def submit_beermat(request):
    if request.method == 'POST':
        form = BeermatSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            beermat = form.save(commit=False)
            beermat.approved = False
            beermat.save()
            return redirect('catalog')
    else:
        form = BeermatSubmissionForm()

    return render(request, 'beermats/submit_beermat.html', {'form': form})


@login_required
def my_collection(request):
    base_items = CollectionItem.objects.filter(user=request.user).select_related('beermat')

    selected_country = request.GET.get('country', 'all')
    selected_beer = request.GET.get('beer', 'all')
    selected_brewery = request.GET.get('brewery', 'all')

    items = base_items
    if selected_country and selected_country != 'all':
        items = items.filter(beermat__country=selected_country)
    if selected_beer and selected_beer != 'all':
        items = items.filter(beermat__beer_name=selected_beer)
    if selected_brewery and selected_brewery != 'all':
        items = items.filter(beermat__brewery=selected_brewery)

    collection_total_beermats = items.count()
    collection_total_countries = items.filter(beermat__country__gt='').values('beermat__country').distinct().count()
    collection_total_brands = items.filter(beermat__beer_name__gt='').values('beermat__beer_name').distinct().count()
    collection_total_breweries = items.filter(beermat__brewery__gt='').values('beermat__brewery').distinct().count()

    countries = base_items
    if selected_beer and selected_beer != 'all':
        countries = countries.filter(beermat__beer_name=selected_beer)
    if selected_brewery and selected_brewery != 'all':
        countries = countries.filter(beermat__brewery=selected_brewery)
    countries = (
        countries
        .filter(beermat__country__gt='')
        .order_by('beermat__country')
        .values_list('beermat__country', flat=True)
        .distinct()
    )
    beers = base_items
    if selected_country and selected_country != 'all':
        beers = beers.filter(beermat__country=selected_country)
    if selected_brewery and selected_brewery != 'all':
        beers = beers.filter(beermat__brewery=selected_brewery)
    beers = (
        beers
        .filter(beermat__beer_name__gt='')
        .order_by('beermat__beer_name')
        .values_list('beermat__beer_name', flat=True)
        .distinct()
    )
    breweries = base_items
    if selected_country and selected_country != 'all':
        breweries = breweries.filter(beermat__country=selected_country)
    if selected_beer and selected_beer != 'all':
        breweries = breweries.filter(beermat__beer_name=selected_beer)
    breweries = (
        breweries
        .filter(beermat__brewery__gt='')
        .order_by('beermat__brewery')
        .values_list('beermat__brewery', flat=True)
        .distinct()
    )

    return render(
        request,
        'beermats/my_collection.html',
        {
            'items': items,
            'countries': countries,
            'beers': beers,
            'breweries': breweries,
            'selected_country': selected_country,
            'selected_beer': selected_beer,
            'selected_brewery': selected_brewery,
            'collection_total_beermats': collection_total_beermats,
            'collection_total_countries': collection_total_countries,
            'collection_total_brands': collection_total_brands,
            'collection_total_breweries': collection_total_breweries,
        },
    )


def _get_collection_stats(request):
    selected_country = request.GET.get('country', 'all')
    selected_beer = request.GET.get('beer', 'all')
    selected_brewery = request.GET.get('brewery', 'all')

    items = CollectionItem.objects.filter(user=request.user)
    if selected_country and selected_country != 'all':
        items = items.filter(beermat__country=selected_country)
    if selected_beer and selected_beer != 'all':
        items = items.filter(beermat__beer_name=selected_beer)
    if selected_brewery and selected_brewery != 'all':
        items = items.filter(beermat__brewery=selected_brewery)

    return {
        'collection_total_beermats': items.count(),
        'collection_total_countries': items.filter(beermat__country__gt='').values('beermat__country').distinct().count(),
        'collection_total_brands': items.filter(beermat__beer_name__gt='').values('beermat__beer_name').distinct().count(),
        'collection_total_breweries': items.filter(beermat__brewery__gt='').values('beermat__brewery').distinct().count(),
    }


@login_required
def profile(request):
    return render(request, 'beermats/profile.html')


@login_required
def profile_settings(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(
        request,
        'beermats/profile_settings.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'beermats/signup.html', {'form': form})


@login_required
def add_to_collection(request, beermat_id):
    beermat = get_object_or_404(Beermat, pk=beermat_id)
    item, created = CollectionItem.objects.get_or_create(user=request.user, beermat=beermat)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response_data = {
            'success': True,
            'action': 'added',
            'collection_item_id': item.id,
            'beermat_id': beermat.id,
            'remove_url': reverse('remove_from_collection', args=[item.id]),
            'add_url': reverse('add_to_collection', args=[beermat.id]),
        }
        response_data.update(_get_collection_stats(request))
        return JsonResponse(response_data)

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'catalog'
    return redirect(next_url)


@login_required
def remove_from_collection(request, item_id):
    item = get_object_or_404(CollectionItem, pk=item_id, user=request.user)
    beermat_id = item.beermat_id
    item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response_data = {
            'success': True,
            'action': 'removed',
            'collection_item_id': item_id,
            'beermat_id': beermat_id,
            'add_url': reverse('add_to_collection', args=[beermat_id]),
        }
        response_data.update(_get_collection_stats(request))
        return JsonResponse(response_data)

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'my_collection'
    return redirect(next_url)
