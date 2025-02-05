from django.db import models
import uuid

class Banner(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    title = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    imgSrc = models.ImageField(upload_to='pubimg/', max_length=255, null=True, blank=True)
    imgWidth =  models.IntegerField(null=True, blank=True)
    imgHeight =  models.IntegerField(null=True, blank=True)
    href = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)