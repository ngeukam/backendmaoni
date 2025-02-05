from django.db import models
import uuid

class Slide(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    bgImg = models.ImageField(upload_to='slideimg/', max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)