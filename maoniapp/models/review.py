from django.db import models
import uuid
from ..services import *
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator

class Review(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    title = models.TextField(max_length=30, null=True, blank=True)
    text = models.TextField(max_length=1000, null=True, blank=True)
    record = models.FileField(upload_to='records/', blank=True, null=True)
    evaluation = models.FloatField(null=True, blank=True)
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='busreview', null=True, blank=True)
    sentiment = models.CharField(max_length=100,null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    authorcountry = models.CharField(max_length=100, null=True, blank=True)
    expdate = models.CharField(max_length=20, null=True, blank=True)
    authorname = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Peut être une adresse e-mail ou un numéro de téléphone"
    )
    language_code = models.CharField(
        max_length=10, 
        null=True, 
        blank=True, 
        default="fr-FR",  # Langue par défaut
        help_text="Langue utilisée pour l'analyse (ex: 'fr-FR', 'en-US')"
    )
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Méthode de validation pour vérifier si le contact est soit un e-mail soit un numéro de téléphone valide.
        """
        if self.contact:
            email_validator = EmailValidator()
            phone_validator = RegexValidator(
                regex=r'^\+?\d{7,15}$',  # Numéro de téléphone international
                message="Entrez un numéro de téléphone valide avec un maximum de 15 chiffres."
            )

            try:
                # Tenter de valider comme une adresse e-mail
                email_validator(self.contact)
            except ValidationError:
                try:
                    # Si ce n'est pas un e-mail, tenter de valider comme numéro de téléphone
                    phone_validator(self.contact)
                except ValidationError:
                    raise ValidationError(
                        {"contact": "Le contact doit être une adresse e-mail ou un numéro de téléphone valide."}
                    )
        
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        # Appeler la méthode de validation avant de sauvegarder
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.business.name} | {self.text[:20]}... | Score: {self.score} | Sentiment: {self.sentiment}"

    