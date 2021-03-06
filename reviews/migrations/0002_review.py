# Generated by Django 3.2 on 2021-05-08 17:43

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0006_alter_table_min_guests'),
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('food', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('service', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('ambience', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('noise', models.CharField(choices=[('S', 'Quiet'), ('M', 'Moderate'), ('L', 'Loud')], max_length=1)),
                ('overall', models.PositiveSmallIntegerField(blank=True, validators=[django.core.validators.MaxValueValidator(5)])),
                ('review', models.CharField(blank=True, max_length=2000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.place')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
