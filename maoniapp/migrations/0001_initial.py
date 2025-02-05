# Generated by Django 5.1.4 on 2025-01-24 18:58

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.TextField(blank=True, max_length=1000, null=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('bgImg', models.ImageField(blank=True, max_length=255, null=True, upload_to='slideimg/')),
                ('url', models.TextField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('role', models.CharField(choices=[('manager', 'Manager'), ('customer', 'Customer'), ('collaborator', 'Collaborator')], default='customer', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_session_key', models.CharField(blank=True, max_length=40, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='maoniapp.category')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('logo', models.ImageField(blank=True, max_length=255, null=True, upload_to='businesslogo/')),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('website', models.CharField(blank=True, max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
                ('btype', models.CharField(blank=True, choices=[('private', 'Private'), ('public', 'Public'), ('parapublic', 'Parapublic')], max_length=50, null=True)),
                ('isverified', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businesscat', to='maoniapp.category')),
            ],
            options={
                'verbose_name': 'Business',
                'verbose_name_plural': 'Businesses',
                'ordering': ['-created_at'],
                'unique_together': {('name', 'category', 'country', 'city')},
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.TextField(blank=True, max_length=30, null=True)),
                ('text', models.TextField(blank=True, max_length=1000, null=True)),
                ('record', models.FileField(blank=True, null=True, upload_to='records/')),
                ('evaluation', models.FloatField(blank=True, null=True)),
                ('sentiment', models.CharField(blank=True, max_length=100, null=True)),
                ('score', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('authorcountry', models.CharField(blank=True, max_length=100, null=True)),
                ('expdate', models.CharField(blank=True, max_length=20, null=True)),
                ('authorname', models.CharField(blank=True, max_length=100, null=True)),
                ('contact', models.CharField(blank=True, help_text='Peut être une adresse e-mail ou un numéro de téléphone', max_length=100, null=True)),
                ('language_code', models.CharField(blank=True, default='fr-FR', help_text="Langue utilisée pour l'analyse (ex: 'fr-FR', 'en-US')", max_length=10, null=True)),
                ('active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='busreview', to='maoniapp.business')),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('text', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='maoniapp.review')),
            ],
        ),
        migrations.CreateModel(
            name='UserBusiness',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maoniapp.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'business')},
            },
        ),
        migrations.AddField(
            model_name='user',
            name='businesses',
            field=models.ManyToManyField(blank=True, related_name='users', through='maoniapp.UserBusiness', to='maoniapp.business'),
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('invitation_code', models.CharField(max_length=10, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businesscodes', to='maoniapp.business')),
            ],
            options={
                'verbose_name': 'Invitation Code',
                'verbose_name_plural': 'Invitation Codes',
                'indexes': [models.Index(fields=['invitation_code'], name='maoniapp_co_invitat_6da0c4_idx')],
            },
        ),
    ]
