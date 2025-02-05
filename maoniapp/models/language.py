from django.db import models

class Language(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="Language code (e.g., 'en', 'fr', 'es')")
    name = models.CharField(max_length=255, help_text="Language name (e.g., 'English', 'Français', 'Español')")

    def __str__(self):
        return self.name

class Translation(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations')
    key = models.CharField(max_length=255, help_text="Translation key (e.g., 'welcomeMessage', 'description')")
    value = models.TextField(help_text="Translated text")

    class Meta:
        unique_together = ('language', 'key')  # Ensure unique key per language

    def __str__(self):
        return f"{self.key} ({self.language.code})"