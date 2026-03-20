from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.shortcuts import get_object_or_404, redirect, render, resolve_url

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
    recent_beermats = Beermat.objects.filter(approved=True).order_by('-approved_at')[:5]
    news_items = NewsItem.objects.filter(published=True).order_by('-published_at')[:5]
    return render(request, 'beermats/home.html', {'recent_beermats': recent_beermats, 'news_items': news_items})


def about(request):
    return render(request, 'beermats/about.html')


def catalog(request):
    beermats = Beermat.objects.filter(approved=True)
    selected_beer = request.GET.get('beer', 'all')
    selected_brewery = request.GET.get('brewery', 'all')

    selected_country = request.GET.get('country', 'all')

    countries = (
        beermats
        .filter(country__gt='')
        .order_by('country')
        .values_list('country', flat=True)
        .distinct()
    )

    beers = (
        CollectionItem.objects.all()
        .filter(beermat__beer_name__gt='')
        .values_list('beermat__beer_name', flat=True)
        .distinct()
        .order_by('beermat__beer_name')
    )

    breweries = (
        CollectionItem.objects.all()
        .filter(beermat__brewery__gt='')
        .values_list('beermat__brewery', flat=True)
        .distinct()
        .order_by('beermat__brewery')
    )
    
    if selected_country and selected_country != 'all':
        beermats = beermats.filter(country=selected_country)
    if selected_beer and selected_beer != 'all':
        beermats = beermats.filter(beer=selected_beer)
    if selected_brewery and selected_brewery != 'all':
        beermats = beermats.filter(brewery=selected_brewery)

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
    items = CollectionItem.objects.filter(user=request.user).select_related('beermat')

    selected_country = request.GET.get('country', 'all')
    selected_beer = request.GET.get('beer', 'all')
    selected_brewery = request.GET.get('brewery', 'all')

    if selected_country and selected_country != 'all':
        items = items.filter(beermat__country=selected_country)
    if selected_beer and selected_beer != 'all':
        items = items.filter(beermat__beer_name=selected_beer)
    if selected_brewery and selected_brewery != 'all':
        items = items.filter(beermat__brewery=selected_brewery)

    countries = (
        CollectionItem.objects.filter(user=request.user)
        .filter(beermat__country__gt='')
        .values_list('beermat__country', flat=True)
        .distinct()
        .order_by('beermat__country')
    )
    beers = (
        CollectionItem.objects.filter(user=request.user)
        .filter(beermat__beer_name__gt='')
        .values_list('beermat__beer_name', flat=True)
        .distinct()
        .order_by('beermat__beer_name')
    )
    breweries = (
        CollectionItem.objects.filter(user=request.user)
        .filter(beermat__brewery__gt='')
        .values_list('beermat__brewery', flat=True)
        .distinct()
        .order_by('beermat__brewery')
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
        },
    )


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
    CollectionItem.objects.get_or_create(user=request.user, beermat=beermat)
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'catalog'
    return redirect(next_url)


@login_required
def remove_from_collection(request, item_id):
    item = get_object_or_404(CollectionItem, pk=item_id, user=request.user)
    item.delete()
    return redirect('my_collection')
