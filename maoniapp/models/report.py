from django.db import models
import uuid
from ..models.business import Business

class Report(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    title = models.TextField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    url = models.TextField(max_length=1000, null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)