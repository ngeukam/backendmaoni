from django.db import models
import uuid
from django.utils.crypto import get_random_string

class Code(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    invitation_code = models.CharField(max_length=10, unique=True)
    business = models.ForeignKey("Business", on_delete=models.CASCADE, related_name='businesscodes')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Invitation Code'
        verbose_name_plural = 'Invitations Codes'
        indexes = [models.Index(fields=['invitation_code'])]  # Ensure an index for `invitation_code`
        
    def __str__(self):
        return f"{self.business.name} | {self.invitation_code} |is used {self.is_active}"
    
    def save(self, *args, **kwargs):
        # Supprimer le code précédent si celui-ci est marqué comme utilisé
        if self.is_active:
            # Supprimer le code déjà utilisé dans la base de données
            Code.objects.filter(invitation_code=self.invitation_code, is_active=True).delete()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code(business):
        # Générer un code unique
        code = get_random_string(length=5).upper()
        while Code.objects.filter(invitation_code=code).exists():  # Vérifier si le code existe déjà
            code = get_random_string(length=5).upper()
        # Crée une nouvelle instance de Code
        return Code.objects.create(invitation_code=code, business=business)