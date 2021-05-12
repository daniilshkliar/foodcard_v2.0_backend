from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password', 'is_active')}),
        ('Personal info', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'phone', 'last_name')
    ordering = ('email',)


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), 
        required=False,
        widget=FilteredSelectMultiple('users', False),
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        self.save_m2m()
        return instance


class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ['permissions']


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)