from django.contrib import admin

from .models import *


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('place', 'date_time', 'phone', 'guests')
    list_filter = ('is_active', 'guests')
    fieldsets = (
        (None, {'fields': ('place', 'table', 'date_time', 'guests')}),
        ('Contacts', {'fields': ('user', 'name', 'phone')}),
        ('Other', {'fields': ('comment', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('place', 'table', 'date_time', 'guests'),
        }),
    )
    search_fields = ('place__title', 'date_time', 'phone')
    ordering = ('place', 'date_time', 'guests')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


admin.site.register(Reservation, ReservationAdmin)