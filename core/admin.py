from django.contrib import admin

from guardian.admin import GuardedModelAdmin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from .models import *


class PlaceAdmin(GuardedModelAdmin, DynamicArrayMixin):
    list_display = ('title', 'country', 'city', 'main_category')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('title', 'is_active')}),
        ('Contacts', {'fields': ('phone', 'website', 'instagram')}),
        ('Address', {'fields': ('country', 'city', 'street', 'coordinates', 'timezone')}),
        # ('Schedule', {'fields': ('opening_hours',)}),
        ('Classification', {'fields': ('main_category', 'additional_categories', 'main_cuisine', 'additional_cuisines', 'additional_services')}),
        ('Other', {'fields': ('description', 'floor')}), #, 'main_photo')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'phone', 'country', 'city', 'street', 'coordinates'),
        }),
    )
    search_fields = ('title', 'country__name', 'city', 'street', 'main_category__name', 'main_cuisine__name')
    ordering = ('country', 'title')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


class AdditionalServiceAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class CuisineAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)


class PlaceImageAdmin(admin.ModelAdmin):
    search_fields = ('place__title',)
    ordering = ('place',)


class MenuImageAdmin(admin.ModelAdmin):
    search_fields = ('place__title',)
    ordering = ('place',)


class TableAdmin(admin.ModelAdmin):
    list_display = ('place', 'number', 'max_guests', 'deposit')
    list_filter = ('max_guests', 'is_vip')
    search_fields = ('place__title', 'max_guests')
    ordering = ('place', 'max_guests')


admin.site.register(Place, PlaceAdmin)
admin.site.register(AdditionalService, AdditionalServiceAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(PlaceImage, PlaceImageAdmin)
admin.site.register(MenuImage, MenuImageAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Favorite)