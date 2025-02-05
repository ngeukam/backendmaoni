from django.db import models
import uuid

from django.forms import JSONField
class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    styles = JSONField()  # Stocke un dictionnaire pour les styles CSS
    href = models.CharField(max_length=200, null=True, blank=True)
    imgSrc = models.CharField(max_length=255, null=True, blank=True)
    imgWidth = models.IntegerField(null=True, blank=True)
    imgHeight = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='subcategories',
        null=True, 
        blank=True
    )  # To enable nested categories

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
