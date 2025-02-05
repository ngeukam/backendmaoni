from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminRole(BasePermission):
    """
    Autorise uniquement les utilisateurs ayant le rôle 'admin'.
    """

    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role == 'manager'


class IsRoleAllowed(BasePermission):
    """
    Autorise uniquement les utilisateurs ayant un rôle spécifique.
    """

    allowed_roles = ['manager', 'collaborator']  # Rôles autorisés

    def has_permission(self, request, view):
        user_role = request.user.role
        return user_role in self.allowed_roles

class IsSuperAdminOrReadOnly(BasePermission):
    """
    Permission permettant seulement aux super administrateurs d'effectuer des actions autres que GET.
    """
    def has_permission(self, request, view):
        # Si la méthode est sûre (GET, HEAD, OPTIONS), tout le monde y a accès
        if request.method in SAFE_METHODS:
            return True
        
        # Vérifie si l'utilisateur est authentifié et est un super administrateur
        return request.user.is_authenticated and request.user.is_superuser
