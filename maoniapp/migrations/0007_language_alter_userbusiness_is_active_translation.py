# Generated by Django 5.1.4 on 2025-02-01 17:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maoniapp', '0006_alter_comment_text_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text="Language code (e.g., 'en', 'fr', 'es')", max_length=10, unique=True)),
                ('name', models.CharField(help_text="Language name (e.g., 'English', 'Français', 'Español')", max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='userbusiness',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text="Translation key (e.g., 'welcomeMessage', 'description')", max_length=255)),
                ('value', models.TextField(help_text='Translated text')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='maoniapp.language')),
            ],
            options={
                'unique_together': {('language', 'key')},
            },
        ),
    ]
