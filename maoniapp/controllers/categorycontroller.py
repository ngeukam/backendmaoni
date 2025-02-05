from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from ..models.category import Category
from .serializers import CategoryBusinessCountSerializer, CategoryNameSerializer, CategorySerializer
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django.db.models import Count, Q


class CustomPagination(PageNumberPagination):
    page_size = 10  # Limit number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum page size

class CategoryFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='icontains', label="Business Name")
    
    class Meta:
        model = Category
        fields = ['name']
        
class FilterCategoryWithNameView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CategoryNameSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CategoryFilter
    pagination_class = CustomPagination

    def get_queryset(self):        
        # Ensure the queryset is ordered by the business name (or another field you prefer)
        queryset = Category.objects.filter(active=True).order_by('name')  # Replace 'name' with any other field if needed
        if not self.request.GET.get('name'):
            return queryset.none()  # Return empty queryset if no name is provided

        return queryset
    
# List and Create Categories
class CategoryListCreateView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
# Retrieve, Update, and Delete a Category
class CategoryRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryBusinessCountView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CategoryBusinessCountSerializer
    def get_queryset(self):
        queryset = Category.objects.filter(active=True).annotate(
            business_count=Count('businesscat', filter=Q(businesscat__active=True)) # Count only active businesses
        ).order_by('-business_count')
        return queryset