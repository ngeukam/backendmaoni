from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.language import Language
from .serializers import TranslationResponseSerializer
from django.utils import timezone
from rest_framework import permissions


class TranslationView(APIView):
    permission_classes = [permissions.AllowAny,]
    def get(self, request):
        language_code = request.GET.get('lang')

        if not language_code:
            return Response({"error": "Language code ('lang') is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            return Response({"error": "Language not found."}, status=status.HTTP_404_NOT_FOUND)

        translations = language.translations.all()

        # For the combined response (Example 5):
        last_updated = timezone.now() # Or get the last updated time of the translations
        serializer = TranslationResponseSerializer({
            'language': language_code,
            'last_updated': last_updated,
            'translations': translations
        })

        return Response(serializer.data, status=status.HTTP_200_OK)