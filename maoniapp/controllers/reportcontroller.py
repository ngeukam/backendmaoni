from rest_framework import generics, permissions
from ..permissions.permissions import IsAdminRole
from ..models.report import Report
from ..models.user import  UserBusiness
from .serializers import ReportSerializer

class UserBusinessReportListView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]  # Require authentication

    def get_queryset(self):
        user = self.request.user
        # Get the businesses the current user is associated with
        user_businesses = UserBusiness.objects.filter(user=user, is_active=True) # Only active businesses

        # Extract business IDs
        business_ids = user_businesses.values_list('business_id', flat=True)

        # Get the reports for those businesses
        reports = Report.objects.filter(business__in=business_ids)
        return reports