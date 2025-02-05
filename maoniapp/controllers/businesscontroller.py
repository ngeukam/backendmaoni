from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..models.review import Review
from ..models.user import User, UserBusiness
from ..permissions.permissions import IsAdminRole, IsRoleAllowed
from ..models.business import Business
from ..models.category import Category
from .serializers import BusinessBrandDisplaySerializer, BusinessDisplaysSerializer, BusinessSerializer, ReviewSerializer, UserBusinessSerializer, UserDisplaySerializer
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as dj_filters
from rest_framework import filters as drf_filters
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import NotFound
from django.db import transaction


class CustomPagination(PageNumberPagination):
    page_size = 10  # Limit number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum page size

# List and Create Businesses
class BusinessListCreateView(ListCreateAPIView):
    queryset = Business.objects.filter(active=True)
    serializer_class = BusinessSerializer

    # Permissions pour la méthode list (pas besoin d'être connecté)
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method == 'POST':
            return [IsAuthenticated(), IsRoleAllowed()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        country = request.data.get('country')
        city = request.data.get('city')
        category_id = request.data.get('category_id')

        # Check for duplicates
        if Business.objects.filter(Q(name=name) & Q(country=country) & Q(city=city) & Q(category_id=category_id)).exists():
            raise ValidationError({
                "error": "A business with the same name, country, category, and city already exists."
            })

        # Start a transaction to ensure atomicity
        with transaction.atomic():
            # Create the business
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            business = serializer.save()

            # Add the current user to the created business
            user = request.user  # Get the current user (make sure user is authenticated)
            user.businesses.add(business)
            user.save()

            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": "Business created successfully and linked to the user!",
                    "data": serializer.data,
                    "error":False
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

class BusinessRetrieveUpdateView(APIView):
    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAuthenticated(), IsAdminRole()]
        return [AllowAny()]

    def get_object(self, business_id):
        try:
            # Filter active businesses
            return Business.objects.filter(pk=business_id, active=True).get()
        except Business.DoesNotExist:
            raise NotFound(detail="Business not found or inactive.")

    def get(self, request, *args, **kwargs):
        business_id = self.kwargs.get('pk')
        business = self.get_object(business_id)
        serializer = BusinessDisplaysSerializer(business)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        business_id = self.kwargs.get('pk')
        business = self.get_object(business_id)
        active_value = request.data.get('active')
        if active_value is not None:
            business.active = active_value.lower() == 'true' #Change business status to false to delete
        serializer = BusinessDisplaysSerializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Business updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
                "message": "Failed to update business.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        business_id = self.kwargs.get('pk')
        business = self.get_object(business_id)
        serializer = BusinessDisplaysSerializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List Businesses Name
class BusinessFilter(dj_filters.FilterSet):
    name = dj_filters.CharFilter(field_name="name", lookup_expr='icontains', label="Business Name")
    
    class Meta:
        model = Business
        fields = ['name']

class BusinessListNameView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = BusinessDisplaysSerializer
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_class = BusinessFilter
    pagination_class = CustomPagination
    def get_queryset(self):
        # Start with filtering active businesses
        queryset = Business.objects.filter(active=True)
        # Get the 'name' parameter from the request
        name = self.request.GET.get('name', '').strip()
        if name:
            # Filter businesses by name if provided
            queryset = queryset.filter(name__icontains=name)
        return queryset

class BusinessWithReviewsListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = BusinessSerializer
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_class = BusinessFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Business.objects.annotate(num_reviews=Count('busreview')).filter(num_reviews__gt=0, active=True)
        
        # Ensure the queryset is ordered by the business name (or another field you prefer)
        queryset = queryset.order_by('name')  # Replace 'name' with any other field if needed

        if not self.request.GET.get('name'):
            return queryset.none()  # Return empty queryset if no name is provided

        return queryset
    
#Récupérer le paramètre 'name' depuis la requête GET pour filtrer par nom d'entreprise
class FilterBusinessReviewsByNameView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, *args, **kwargs):
        businessname = request.GET.get('businessname', None)
        
        # Build the query with the conditions provided
        filters = {'active': True}
 
        if businessname:
            filters['name__icontains'] = businessname  # Case-insensitive search
        
        # Retrieve businesses with the provided filters
        businesses = Business.objects.filter(**filters)
        # Pagination
        paginator = CustomPagination()
        page = paginator.paginate_queryset(businesses, request)
        
        if page is not None:
            # Serialize the paginated data
            serializer = BusinessSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # If no pagination, return all results
        serializer = BusinessSerializer(businesses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BusinessDetailView(APIView):
    permission_classes = [AllowAny,]
    def get(self, request, *args, **kwargs):
        businesscategory = request.GET.get('businesscategory', None)
        businesscountry = request.GET.get('country', None)
        businesscity = request.GET.get('city', None)
        businessname = request.GET.get('businessname', None)
        
        # Get Category
        try: 
            category = Category.objects.get(name=businesscategory)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found"}, status=status.HTTP_400_BAD_REQUEST)
        # Retrieve the business based on the filters
        business = Business.objects.filter(
            country=businesscountry, 
            city=businesscity, 
            name=businessname, 
            category=category,
            active=True
        ).first()

        if not business:
            return Response({"detail": "Business not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the business data
        serializer = BusinessSerializer(business)  # if 'business' is a single object, use 'many=False'
        return Response(serializer.data)

#Get all related business
class RelatedBusinessesView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, business_id):
        try:
            # Get the business object by id
            business = Business.objects.get(id=business_id, active=True)
        except Business.DoesNotExist:
            return Response({"detail": "Business not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get related businesses using the get_related_businesses method
        related_businesses = business.get_related_businesses()

        # Serialize the related businesses
        serializer = BusinessSerializer(related_businesses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetAllBusinessByCategory(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, categoryName):
        try:
            # Retrieve the category
            category = Category.objects.get(name=categoryName)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve businesses under the category
        businesses = Business.objects.filter(
            category=category, active=True, showeval=True).annotate(num_reviews=Count('busreview')).filter(num_reviews__gt=0)
        if not businesses.exists():
            return Response({"detail": "No businesses found for this category."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the businesses
        serializer = BusinessSerializer(businesses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserBusinessesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessDisplaysSerializer

    def get(self, request):
        # Get the logged-in user's businesses and filter for active ones
        user = request.user
        businesses = user.businesses.filter(active=True)  # Only fetch active businesses
        
        # Serialize the businesses
        serializer = self.serializer_class(businesses, many=True)
        return Response(serializer.data)

class UsersInSameBusinessView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDisplaySerializer

    def get(self, request):
        # Get the logged-in user's active businesses
        user_businesses = request.user.businesses.filter(active=True)  # Only active businesses
        # Get all users linked to the same businesses, excluding the current user
        users = User.objects.filter(businesses__in=user_businesses).exclude(id=request.user.id).distinct()
        # Serialize the user data
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChangeUserBusinessView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, *args, **kwargs):
        # Récupérer l'utilisateur
        try:
            user_id = kwargs.get('user_id')
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer les données de la requête
        business_ids = request.data.get("business_ids", [])
        # is_active = request.data.get("is_active", False)
        if not isinstance(business_ids, list) or not business_ids:
            return Response({"detail": "Invalid or missing business."}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer toutes les entreprises correspondantes
        businesses = Business.objects.filter(id__in=business_ids)
        existing_ids = businesses.values_list('id', flat=True)
        existing_ids = {str(b_id) for b_id in existing_ids}
        missing_ids = set(business_ids) - existing_ids

        if missing_ids:
            return Response(
                {"detail": f"Some businesses not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Récupérer toutes les relations existantes entre l'utilisateur et les entreprises
        existing_relations = UserBusiness.objects.filter(user=user, business__id__in=business_ids)
        existing_business_ids = existing_relations.values_list('business_id', flat=True)

        # Traiter les entreprises
        updated_relations = []
        for business in businesses:
            if business.id in existing_business_ids:
                 pass
            else:
                # Créer une nouvelle relation
                user_business = UserBusiness(user=user, business=business, is_active=False)
                user_business.save()

                updated_relations.append(user_business)

        # Sérialiser les relations mises à jour
        serializer = UserBusinessSerializer(updated_relations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteUserBusinessView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    def delete(self, request, user_id, business_id):
        # Vérification de l'existence de l'enregistrement
        user_business = get_object_or_404(UserBusiness, user_id=user_id, business_id=business_id)
        # Suppression de l'enregistrement
        user_business.delete()
        
        return Response(
            {"message": f"The relationship between user {user_id} and business {business_id} has been deleted.", "error":False},
            status=status.HTTP_200_OK 
        )

class BusinessBrandListView(APIView):
    permission_classes = [AllowAny,]
    """
    View to get all businesses brand
    """
    def get(self, request, *args, **kwargs):
        # Retrieve all business records
        businesses = Business.objects.filter(active=True).all()

        # Serialize the data
        serializer = BusinessBrandDisplaySerializer(businesses, many=True)

        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserBusinessReviews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get all businesses for the current user
        user_businesses = UserBusiness.objects.filter(user=request.user, is_active=True)
        # Collect all business IDs associated with the user
        business_ids = user_businesses.values_list('business', flat=True)

        # Get all reviews for these businesses
        reviews = Review.objects.filter(business__in=business_ids, active=True)

        # Serialize the reviews
        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data)


class BusinessFilter(dj_filters.FilterSet):
    category = dj_filters.CharFilter(field_name='category__name', lookup_expr='exact')  # Exact match for category
    country = dj_filters.CharFilter(field_name='country', lookup_expr='icontains') # Case-insensitive contains
    city = dj_filters.CharFilter(field_name='city', lookup_expr='icontains')  # Case-insensitive contains
    # Add other filters as needed (e.g., name, other fields)

    class Meta:
        model = Business
        fields = ['category', 'country', 'city']  # List ALL filterable fields

    def filter_queryset(self, queryset):
        category = self.request.GET.get('category')
        country = self.request.GET.get('country')
        city = self.request.GET.get('city')

        queryset = queryset.filter(active=True, showeval=True)  # Initial filters

        if category:
            queryset = queryset.filter(category__name=category)
        if country:
            queryset = queryset.filter(country__icontains=country)
        if city:
            queryset = queryset.filter(city__icontains=city)

        queryset = queryset.annotate(num_reviews=Count('busreview')).filter(num_reviews__gt=0)
        return queryset

class BusinessListView(ListAPIView):
    queryset = Business.objects.all()  # Or pre-filter if always needed
    serializer_class = BusinessSerializer
    filter_backends = [dj_filters.DjangoFilterBackend]  # ONLY DjangoFilterBackend
    filterset_class = BusinessFilter

