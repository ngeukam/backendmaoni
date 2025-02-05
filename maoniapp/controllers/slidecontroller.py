from rest_framework import viewsets
from ..models.slide import Slide
from .serializers import SlideSerialiazer
from ..permissions.permissions import IsSuperAdminOrReadOnly

class SlideViewSet(viewsets.ModelViewSet):
    queryset = Slide.objects.all()
    serializer_class = SlideSerialiazer
    permission_classes = [IsSuperAdminOrReadOnly]

