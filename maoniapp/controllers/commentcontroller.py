from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models.user import UserBusiness
from ..models.comment import Comment
from ..models.review import Review
from .serializers import CommentSerializer
from ..permissions.permissions import IsRoleAllowed


class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated, IsRoleAllowed]

    def post(self, request, *args, **kwargs):
        review_id = kwargs.get('review_id')  # Get review ID from URL parameters
        user = request.user  # Get the authenticated user

        # Validate review existence
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is active in any UserBusiness
        is_active_user = UserBusiness.objects.filter(user=user, is_active=True).exists()
        if not is_active_user:
            return Response({"error": "You are not authorized to create a comment."}, status=status.HTTP_403_FORBIDDEN)

        # Prepare data for serializer
        data = request.data.copy()
        data['review'] = review.id
        data['user'] = user.id

        # Serialize and save the comment
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated,]
