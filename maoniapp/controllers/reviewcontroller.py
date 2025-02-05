from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView

from ..permissions.permissions import IsAdminRole
from ..models.review import Review
from ..models.business import Business, Code
from .serializers import CommentSerializer, ReviewSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from ..models.category import Category
from rest_framework.exceptions import NotFound


class CustomPagination(PageNumberPagination):
    page_size = 10  # Limit number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum page size

# List and Create Reviews
class ReviewListCreateView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Review.objects.filter(active=True,  business__showreview=True).order_by('-created_at')[:4]
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        # Récupérer le code d'invitation depuis la requête
        invitation_code = request.data.get("invitation_code")

        if invitation_code:
            try:
                # Vérifier si le code d'invitation existe et est actif
                code = Code.objects.filter(invitation_code=invitation_code, is_active=True).first()

                if not code:
                    return Response(
                        {"detail": "Invalid or inactive invitation code."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                code.is_active = False
                code.save()
                # Proceed with creating the review
                return super().create(request, *args, **kwargs)
            
            except APIException as api_err:
                # Handle API specific errors
                return Response(
                    {"detail": str(api_err)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as err:
                # Catch all other exceptions
                return Response(
                    {"detail": f"An error occurred: {str(err)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"detail": "Invitation code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ReviewListByBusinessView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        businesscategory = request.GET.get('businesscategory', None)
        businesscountry = request.GET.get('country', None)
        businesscity = request.GET.get('city', None)
        businessname = request.GET.get('businessname', None)
        filters = {'active': True}

        if businesscategory:
            try:
                category = Category.objects.get(name=businesscategory)
                filters['category'] = category
            except Category.DoesNotExist:
                return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        if businesscountry:
            filters['country'] = businesscountry
        if businesscity:
            filters['city'] = businesscity
        if businessname:
            filters['name__icontains'] = businessname
        
        business_id = Business.objects.filter(**filters).values_list('id', flat=True)
        business_reviews = Review.objects.filter(business_id__in=business_id, active=True)
        
        # Pagination
        paginator = CustomPagination()
        page = paginator.paginate_queryset(business_reviews, request)
        
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
       
        serializer = ReviewSerializer(business_reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ReviewCommentsView(APIView):
    permission_classes = [AllowAny,]
    def get(self, request, review_id):
        try:
            # Fetch the review
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"detail": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get related comments
        comments = review.comments.all()[0:]
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReviewUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    def get_object(self, reviewId):
        try:
            # Filter active businesses
            return Review.objects.filter(pk=reviewId, active=True).get()
        except Review.DoesNotExist:
            raise NotFound(detail="Review not found or inactive.")
        
    def put(self, request, *args, **kwargs):
        reviewId = self.kwargs.get('reviewId')
        review = self.get_object(reviewId)
        active_value = request.data.get('active')
        if active_value is not None:
            review.active = active_value.lower() == 'true' #Change business status to false to delete
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Review updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
                "message": "Failed to update Review.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)