from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.business import Code
from rest_framework.permissions import AllowAny

class CheckCodeStatusView(APIView):
    permission_classes = [AllowAny,]
    def get(self, request, invitation_code, format=None):
        try:
            # Check if the code exists
            code = Code.objects.get(invitation_code=invitation_code)
            
            # Return whether the code is active or not
            return Response({'is_active': code.is_active}, status=status.HTTP_200_OK)
        except Code.DoesNotExist:
            return Response({'detail': 'Code not found.'}, status=status.HTTP_404_NOT_FOUND)
