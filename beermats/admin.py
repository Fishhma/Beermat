from django.contrib import admin

from .models import Beermat, CollectionItem, NewsItem, Profile


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'published_at', 'created_at')
    list_filter = ('published',)
    search_fields = ('title', 'body')
    readonly_fields = ('created_at', 'updated_at', 'published_at')


@admin.register(Beermat)
class BeermatAdmin(admin.ModelAdmin):
    list_display = ('name', 'beer_name', 'brewery', 'country', 'approved', 'approved_at', 'created_at')
    list_filter = ('approved', 'brewery', 'country')
    search_fields = ('name', 'beer_name', 'brewery', 'country')
    readonly_fields = ('created_at', 'approved_at')
    exclude = ('style', 'photo_front_thumb', 'photo_back_thumb')


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'beermat', 'acquired_at')
    list_filter = ('user',)
    search_fields = ('beermat__name', 'user__username')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')
