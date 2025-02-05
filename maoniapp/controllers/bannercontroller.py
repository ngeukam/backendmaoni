from rest_framework import viewsets
from ..permissions.permissions import IsSuperAdminOrReadOnly
from ..models.banner import Banner
from .serializers import BannerSerialiazer

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerialiazer
    permission_classes = [IsSuperAdminOrReadOnly]
