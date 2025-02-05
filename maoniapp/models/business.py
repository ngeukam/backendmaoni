from decimal import Decimal
from django.db import models
import uuid
from django.db.models import Avg, Count, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models.code import Code

class Business(models.Model):
    class BTypeChoices(models.TextChoices):
        PRIVATE = 'private', 'Private'
        PUBLIC = 'public', 'Public'
        PARAPUBLIC = 'parapublic', 'Parapublic'
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    logo = models.ImageField(upload_to='businesslogo/', max_length=255, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='businesscat')
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    btype = models.CharField(
        max_length=50,
        choices=BTypeChoices.choices,
        null=True,
        blank=True
    )
    isverified = models.BooleanField(default=False)
    showeval = models.BooleanField(default=True)
    showreview = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'
        unique_together = ('name', 'category', 'country', 'city')
        ordering = ['-created_at']
    def get_reviews_info(self):
        reviews = self.busreview.all()  # Get all reviews related to this business
        total_reviews = reviews.count()
        total_evaluation = reviews.aggregate(average_evaluation=Avg('evaluation'))['average_evaluation'] or 0
        has_reviews = total_reviews > 0
        
        # Round total_evaluation to 2 decimal places
        total_evaluation = round(Decimal(total_evaluation), 2)
        
        return {
            "total_reviews": total_reviews,
            "total_evaluation": total_evaluation,
            "has_reviews": has_reviews
        }
        
    def get_related_businesses(self):
        # Retrieve all businesses from the same category, city, and country, excluding this business
        return (
            Business.objects.filter(
                Q(category=self.category)
            )
            .annotate(total_reviews=Count('busreview'))  # Annoter le nombre de reviews
            .filter(total_reviews__gt=0)  # Inclure uniquement les entreprises ayant des avis
            .exclude(id=self.id)[:5]  ## Exclude the current business
        )
    @receiver(post_save, sender='maoniapp.Business')
    def generate_codes_for_new_business(sender, instance, created, **kwargs):
        if created:
            for _ in range(32):
                Code.generate_code(business=instance)
                
    def __str__(self):
        return f"{self.name} | {self.category.name} | {self.country} | {self.city}"