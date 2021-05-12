from smtplib import SMTPAuthenticationError

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def _create_user(self, email, phone, password=None, **extra_fields):
        """
        Create and save a user with the given email, phone number and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not phone:
            raise ValueError('Users must have a phone number')

        user = self.model(email=self.normalize_email(email), phone=phone, **extra_fields)

        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, phone, password, **extra_fields)

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A class implementing a fully featured User model with admin-compliant permissions.

    Email, phone number and password are required. Other fields are optional.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone = PhoneNumberField(unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Return the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this user.
        """
        try:
            send_mail(subject, message, from_email, [self.email], **kwargs)
        except SMTPAuthenticationError:
            raise